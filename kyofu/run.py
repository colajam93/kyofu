from kyofu.metadata import Metadata
from pathlib import Path
from kyofu.model import Song, Library
from typing import Iterable


def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest='sub_command')

    init_parser = subparsers.add_parser('init')
    init_parser.add_argument('library_name')
    init_parser.add_argument('base_path')
    init_parser.set_defaults(func=init)

    scan_parser = subparsers.add_parser('scan')
    scan_parser.add_argument('library_name')
    scan_parser.add_argument('--overwrite-song', action='store_true')
    scan_parser.add_argument('--path-hint', '-p', action='append')
    scan_parser.set_defaults(func=scan)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('library_name')
    update_parser.set_defaults(func=update)

    return parser.parse_args()


def _import_song(library: Library, metadata: Metadata, song: Song = None) -> Song:
    if not song:
        song = Song()
        song.library_id = library.library_id
        song.file_path = str(library.relative_path(metadata.file.path))
    else:
        assert song.library_id == library.library_id
        assert str(song.file_path) == str(library.relative_path(metadata.file.path))
    song.title = metadata.song.title
    song.album = metadata.song.album
    song.artist = metadata.song.artist
    song.album_artist = metadata.song.album_artist
    song.genre = metadata.song.genre
    song.track_number = metadata.song.track_number
    song.disc_number = metadata.song.disc_number
    song.release_year = metadata.song.year
    song.modified = metadata.file.modified

    return song


def _full_scan(path: Path, path_hint: Iterable[str]) -> Iterable[Path]:
    if path_hint:
        for hint in path_hint:
            target_path = path / Path(hint)
            for p in target_path.rglob('*'):
                if p.is_dir():
                    continue
                yield p
    else:
        for p in path.rglob('*'):
            if p.is_dir():
                continue
            yield p


def _full_sync(library: Library, overwrite: bool = False, path_hint: Iterable[str] = None):
    from kyofu.metadata import load_metadata
    from kyofu import session, logger
    from sqlalchemy import or_

    if path_hint:
        query = session.query(Song)
        query = query.filter(Song.library_id == library.library_id)
        query = query.filter(
            or_(Song.file_path.like(f'{h}%') for h in path_hint)
        )
        imported = {s.file_path: s for s in query.all()}
    else:
        imported = {s.file_path: s for s in library.song}
    exists = set()

    for p in _full_scan(library.path, path_hint):
        metadata = load_metadata(p)
        if not metadata:
            continue
        relative_path = library.relative_path(metadata.file.path)
        if str(relative_path) in imported:
            exists.add(str(relative_path))
            if overwrite:
                _import_song(library, metadata, song=imported.get(str(relative_path)))
                logger.info(f'Force updated: path={p}')
        else:
            song = _import_song(library, metadata)
            logger.info(f'Added: path={p}')
            session.add(song)

    deleted = set(imported.keys()) - exists
    for p in deleted:
        dp = Path(p)
        if not dp.exists():
            logger.info(f'Deleted: path={p}')
            session.delete(Song.get_by_path(dp))

    session.commit()


def init(args):
    from kyofu import session

    base_path = Path(args.base_path).resolve()
    name = args.library_name

    library = Library(name=name, base_path=str(base_path))
    session.add(library)
    session.commit()

    _full_sync(library)


def scan(args):
    from kyofu.model import Library

    name = args.library_name
    overwrite = args.overwrite_song
    path_hint = args.path_hint

    library = Library.get_by_name(name)
    if path_hint:
        for h in path_hint:
            hp = library.path / h
            if not hp.exists():
                raise FileNotFoundError(hp)

    _full_sync(library, overwrite, path_hint)


def _diff_scan(library: Library) -> Iterable[Path]:
    from kyofu import session
    from kyofu.exceptions import KyofuError
    from sqlalchemy.sql.functions import max
    import subprocess
    from datetime import datetime

    query = session.query(max(Song.modified))
    query = query.filter(Song.library_id == library.library_id)
    (last_modified,) = query.first()
    now = datetime.now()
    delta = now - last_modified
    buffer_minute = 0
    delta_minute = delta.days * 24 * 60 + delta.seconds // 60 + buffer_minute

    result = subprocess.run(['find', library.base_path, '-type', 'f', '-mmin', f'-{delta_minute}'],
                            capture_output=True)
    if result.returncode != 0:
        raise KyofuError(result.stderr.decode())

    raw_output = result.stdout.decode().strip()
    if not raw_output:
        return ()
    for p in raw_output.split('\n'):
        yield Path(p)


def update(args):
    from kyofu.metadata import load_metadata
    from kyofu import session, logger

    name = args.library_name
    library = Library.get_by_name(name)

    if len(library.song) == 0:
        logger.info(f'No song in library. try full scan: library={library}')
        return scan(args)

    for path in _diff_scan(library):
        metadata = load_metadata(path)
        relative_path = library.relative_path(path)
        song = Song.get_by_path(relative_path)
        if song:
            logger.info(f'Updated: path={relative_path}')
            _import_song(library, metadata, song=song)
        else:
            logger.info(f'Added: path={relative_path}')
            song = _import_song(library, metadata)
            session.add(song)

    session.commit()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
