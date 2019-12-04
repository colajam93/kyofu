import pickle
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from mutagen import File

from kyofu import logger
from kyofu.exceptions import KyofuError


class MetadataError(KyofuError):
    pass


@dataclass
class Fraction:
    numerator: int
    denominator: int


@dataclass
class SongMetadata:
    title: str
    album: str
    artist: str
    album_artist: Optional[str]
    genre: str
    track_number: int
    disc_number: int
    year: int


@dataclass
class FileMetadata:
    _DUMP_FILE_EXTENSION = '.pickle'

    raw_path: Path
    file_type: str
    modified: datetime

    @property
    def raw_path_str(self):
        return str(self.raw_path)

    @property
    def is_dump_file(self):
        return self.raw_path_str.endswith(self._DUMP_FILE_EXTENSION)

    @property
    def path(self):
        if self.is_dump_file:
            return Path(self.raw_path_str[:len(self.raw_path_str) - len(self._DUMP_FILE_EXTENSION)])
        else:
            return self.raw_path


@dataclass
class Metadata:
    song: SongMetadata
    file: FileMetadata


def _guess_file_type(file: File) -> str:
    if 'audio/mp3' in file.mime:
        return 'mp3'
    elif 'audio/flac' in file.mime:
        return 'flac'
    elif 'audio/aac' in file.mime:
        return 'aac'
    else:
        logger.warning('Unknown file type %s' % file.mime)
        return file.mime[0]


def _as_fraction(num: str) -> Fraction:
    if '/' in num:
        n, d, *_ = num.split('/')
        return Fraction(int(n), int(d))
    else:
        return Fraction(int(num), 1)


def _as_year(date: str) -> int:
    try:
        return int(date[:4])
    except ValueError as e:
        raise MetadataError(f'parse year failed: error={e}')


class MetadataExtractor:
    def __init__(self, file: File, path: Path, file_type: str):
        self.path = path
        self.file = file
        self.file_type = file_type

    @property
    def disc_number(self) -> int:
        field = self._extract_field('discnumber')
        if field:
            return _as_fraction(field).numerator
        return 1

    @property
    def track_number(self) -> int:
        field = self._extract_field('tracknumber', required=True)
        return _as_fraction(field).numerator

    @property
    def title(self) -> str:
        return self._extract_field('title', required=True)

    @property
    def album(self) -> str:
        return self._extract_field('album', required=True)

    @property
    def artist(self) -> str:
        return self._extract_field('artist', required=True)

    @property
    def album_artist(self) -> Optional[str]:
        field = self._extract_field('albumartist')
        return field if field else None

    @property
    def genre(self) -> str:
        return self._extract_field('genre', required=True)

    @property
    def year(self) -> int:
        return _as_year(self._extract_field('date', required=True))

    def as_metadata(self) -> Metadata:
        title = self.title
        album = self.album
        artist = self.artist
        album_artist = self.album_artist
        genre = self.genre
        track_number = self.track_number
        disc_number = self.disc_number
        year = self.year

        song_metadata = SongMetadata(
            title=title,
            album=album,
            artist=artist,
            album_artist=album_artist,
            genre=genre,
            track_number=track_number,
            disc_number=disc_number,
            year=year,
        )
        file_metadata = self.as_file_metadata()

        return Metadata(
            song=song_metadata,
            file=file_metadata,
        )

    def _extract_field(self, key: str, required=False) -> str:
        result = self.file.tags.get(key)
        if required and not result:
            raise MetadataError('missing field: key=%s' % key)
        if not result:
            return ''

        if len(result) > 1:
            logger.warning('multiple values found: key=%s' % key)

        return result[0]

    def as_file_metadata(self) -> FileMetadata:
        return FileMetadata(
            raw_path=self.path.resolve(),
            file_type=self.file_type,
            modified=datetime.fromtimestamp(self.path.stat().st_mtime)
        )


def _load_metadata(path: Path) -> Optional[Metadata]:
    if path.suffix == '.pickle':
        with path.open('rb') as f:
            try:
                guessed_file = pickle.load(f)
            except Exception as e:
                logger.warning(f'failed to load pickle: path={path} error={e}')
                return None
    else:
        with path.open('rb') as f:
            guessed_file = File(f, easy=True)
        if not guessed_file:
            logger.warning('Failed to guess file type: %s' % path)
            return None

    if 'audio/mp3' in guessed_file.mime:
        metadata = MetadataExtractor(guessed_file, path, 'mp3').as_metadata()
    elif 'audio/flac' in guessed_file.mime:
        metadata = MetadataExtractor(guessed_file, path, 'flac').as_metadata()
    elif 'audio/aac' in guessed_file.mime:
        metadata = MetadataExtractor(guessed_file, path, 'aac').as_metadata()
    else:
        logger.error('Unknown file type %s' % guessed_file.mime)
        return None

    return metadata


def load_metadata(path: Path) -> Optional[Metadata]:
    from kyofu import logger

    try:
        return _load_metadata(path)
    except Exception as e:
        logger.warning(f'Failed to load metadata: path={path}, error={e}')
        return None


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('file')
    return parser.parse_args()


def _main() -> None:
    args = _parse_args()
    target_path = Path(args.file)
    try:
        metadata = load_metadata(target_path)
        print(asdict(metadata))
    except Exception as e:
        logger.error(f'path={target_path} exception={e}')


if __name__ == '__main__':
    _main()
