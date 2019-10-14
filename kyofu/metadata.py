import pickle
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from datetime import datetime

from mutagen import File

from kyofu import logger


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
    path: str
    file_type: str
    modified_at: datetime


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


def _get_number(num: str) -> int:
    return int(num.split('/')[0])


class MetadataExtractable(metaclass=ABCMeta):
    def __init__(self, path: Path):
        self.path = path

    @property
    @abstractmethod
    def file_type(self) -> str:
        pass

    @abstractmethod
    def as_metadata(self) -> Metadata:
        pass

    def as_file_metadata(self) -> FileMetadata:
        return FileMetadata(
            path=str(self.path.resolve()),
            file_type=self.file_type,
            modified_at=datetime.fromtimestamp(self.path.stat().st_mtime)
        )


class MP3MetadataExtractor(MetadataExtractable):
    file_type = 'mp3'

    def __init__(self, file: File, path: Path) -> None:
        super().__init__(path)
        self.file: File = file

    def _extract_field(self, key: str, required=False) -> str:
        result = self.file.tags.get(key)
        if required and not result:
            logger.error('missing field: key=%s' % key)
            return ''
        if not result:
            logger.info('missing field: key=%s' % key)
            return ''

        if len(result) > 1:
            logger.warning('multiple values found: key=%s' % key)

        return result[0]

    @staticmethod
    def _as_fraction(num: str) -> Fraction:
        if '/' in num:
            n, d, *_ = num.split('/')
            return Fraction(int(n), int(d))
        else:
            return Fraction(int(num), 1)

    @property
    def disc_number(self) -> int:
        field = self._extract_field('discnumber')
        if field:
            return self._as_fraction(field).numerator
        return 1

    @property
    def track_number(self) -> int:
        field = self._extract_field('tracknumber', required=True)
        return self._as_fraction(field).numerator

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
        return self._extract_field('album_artist')

    @property
    def genre(self) -> str:
        return self._extract_field('genre', required=True)

    @property
    def year(self) -> int:
        return int(self._extract_field('date', required=True))

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


class FLACMetadataExtractor(MetadataExtractable):
    file_type = 'flac'

    def __init__(self, file: File, path: Path) -> None:
        super().__init__(path)
        self.file = file

    def _extract_field(self, key: str, required=False, default=None) -> str:
        result = self.file.tags.get(key)
        if required and not result:
            logger.error('missing field: key=%s' % key)
            return ''
        if not result:
            if default:
                return default
            else:
                logger.info('missing field: key=%s' % key)
                return ''

        if len(result) > 1:
            logger.warning('multiple values found: key=%s' % key)

        return result[0]

    def as_metadata(self) -> Metadata:
        title = self._extract_field('title', required=True)
        album = self._extract_field('album', required=True)
        artist = self._extract_field('artist', required=True)
        album_artist = self._extract_field('album_artist')
        genre = self._extract_field('genre', required=True)
        track_number = _get_number(self._extract_field('tracknumber', required=True))
        disc_number = _get_number(self._extract_field('discnumber', default='1'))
        year = _get_number(self._extract_field('date', required=True))

        song_metadata = SongMetadata(
            title=title,
            album=album,
            artist=artist,
            album_artist=album_artist,
            genre=genre,
            track_number=track_number,
            disc_number=disc_number,
            year=year
        )

        return Metadata(
            song=song_metadata,
            file=self.as_file_metadata()
        )


class AACMetadaExtractor(MetadataExtractable):
    file_type = 'aac'

    def __init__(self, file: File, path: Path) -> None:
        super().__init__(path)
        self.file = file

    def as_metadata(self) -> Metadata:
        pass


def load_metadata(path: Path) -> Optional[Metadata]:
    if path.suffix == '.pickle':
        with path.open('rb') as f:
            guessed_file = pickle.load(f)
    else:
        with path.open('rb') as f:
            guessed_file = File(f, easy=True)
        if not guessed_file:
            logger.warning('Failed to guess file type: %s' % path)
            return None

    logger.info(guessed_file.tags)

    if 'audio/mp3' in guessed_file.mime:
        metadata = MP3MetadataExtractor(guessed_file, path).as_metadata()
    elif 'audio/flac' in guessed_file.mime:
        metadata = FLACMetadataExtractor(guessed_file, path).as_metadata()
    elif 'audio/aac' in guessed_file.mime:
        metadata = AACMetadaExtractor(guessed_file, path).as_metadata()
    else:
        logger.error('Unknown file type %s' % guessed_file.mime)
        return None

    logger.info(asdict(metadata))


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('file')
    return parser.parse_args()


def _main() -> None:
    args = _parse_args()
    target_path = Path(args.file)
    try:
        load_metadata(target_path)
    except Exception as e:
        logger.error(f'path={target_path} exception={e}')


if __name__ == '__main__':
    _main()
