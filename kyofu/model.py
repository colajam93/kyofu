from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

Base = declarative_base()
sqla_metadata = Base.metadata


class ExportableMixin:
    def as_dict(self):
        result = {}
        if hasattr(self, 'exclude_column'):
            exclude = set(self.exclude_column)
        else:
            exclude = set()

        for m in self.__table__.columns:
            key = m.key
            if key in exclude:
                continue
            result[key] = getattr(self, key)
        return result


class Library(Base):
    __tablename__ = 'library'

    library_id = Column(INTEGER(20), primary_key=True)
    name = Column(String(100, 'utf8mb4_unicode_ci'), nullable=False)
    base_path = Column(String(500, 'utf8mb4_unicode_ci'), nullable=False)
    song = relationship('Song', back_populates='library')

    def relative_path(self, path: Path) -> Path:
        return path.relative_to(Path(self.base_path))

    @property
    def path(self) -> Path:
        return Path(self.base_path)

    @staticmethod
    def get_by_name(name: str, required: bool = False) -> 'Library':
        from kyofu import session
        from kyofu.exceptions import EntityNotFoundError

        query = session.query(Library)
        query = query.filter(Library.name == name)
        library = query.first()
        if not library and required:
            raise EntityNotFoundError(f'Library not found: name={name}')
        return library


class Song(Base):
    __tablename__ = 'song'

    song_id = Column(INTEGER(20), primary_key=True)
    library_id = Column(ForeignKey('library.library_id', onupdate='CASCADE'), nullable=False, index=True)
    title = Column(String(200, 'utf8mb4_unicode_ci'), nullable=False, index=True)
    album = Column(String(200, 'utf8mb4_unicode_ci'), nullable=False, index=True)
    artist = Column(String(200, 'utf8mb4_unicode_ci'), nullable=False, index=True)
    album_artist = Column(String(200, 'utf8mb4_unicode_ci'), index=True)
    genre = Column(String(50, 'utf8mb4_unicode_ci'), nullable=False, index=True)
    track_number = Column(SMALLINT(2), nullable=False)
    disc_number = Column(SMALLINT(2), nullable=False)
    release_year = Column(SMALLINT(4), nullable=False)
    modified = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    file_path = Column(String(500, 'utf8mb4_unicode_ci'), nullable=False, unique=True)

    library = relationship('Library', back_populates='song')

    @staticmethod
    def get_by_path(path: Path, required: bool = False) -> 'Song':
        from kyofu import session
        from kyofu.exceptions import EntityNotFoundError

        query = session.query(Song)
        query = query.filter(Song.file_path == str(path))
        result = query.first()

        if not result and required:
            raise EntityNotFoundError(path)

        return result
