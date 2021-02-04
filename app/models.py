from sqlalchemy import (create_engine, Date, Table, Column, Integer, String,
                        ForeignKey)
from sqlalchemy.orm import relationship

from .database import Base

link_table_a = Table('link_package_developer', Base.metadata,
            Column('package_id', Integer, ForeignKey('package.id')),
            Column('developer_id', Integer, ForeignKey('developer.id'))
    )


link_table_b = Table('link_defconfig_developer', Base.metadata,
            Column('defconfig_id', Integer, ForeignKey('defconfig.id')),
            Column('developer_id', Integer, ForeignKey('developer.id'))
    )


class Common(Base):
    __tablename__ = 'common'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)


class Developer(Base):
    __tablename__ = 'developer'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    gravatar_url = Column(String)

    packages = relationship('Package', secondary='link_package_developer')
    defconfigs = relationship('Defconfig', secondary='link_defconfig_developer')

    def __repr__(self):
       return "<Developer(name='%s', email='%s')>" % (self.name, self.email)


class Package(Base):
    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    current_version = Column(String)
    latest_version = Column(String)
    latest_version_id = Column(Integer)
    path = Column(String)
    pkg_path = Column(String)
    cpeid = Column(String)
    url = Column(String)
    license = Column(String)
    patch_count = Column(Integer)
    developer_count = Column(Integer)
    cve_count = Column(Integer)
    status_ok = Column(Integer)
    status_warning = Column(Integer)
    status_error = Column(Integer)

    developers = relationship('Developer', secondary='link_package_developer')
    status = relationship("Status", back_populates="package")
    patches = relationship("Patch", back_populates="package")
    cves = relationship("Cve", back_populates="package")
    infras = relationship("Infrastructure", back_populates="package")

    def __repr__(self):
       return "<Package(name='%s')>" % (self.name)


class Infrastructure(Base):
    __tablename__ = 'infrastructures'

    id = Column(Integer, primary_key=True)
    destination = Column(String)
    build_system = Column(String)
    parent_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", back_populates="infras")

    def __repr__(self):
       return "<Infra(destination='%s' - build_system='%s')>" % (self.destination, self.build_system)


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True)
    check = Column(String)
    result = Column(String)
    verbose = Column(String)
    parent_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", back_populates="status")

    def __repr__(self):
       return "<Status(check='%s' - result='%s' - versose='%s')>" % (self.check, self.result, self.verbose)


class Patch(Base):
    __tablename__ = 'patch'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    parent_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", back_populates="patches")

    def __repr__(self):
       return "<Status(name='%s %s %s')>" % (self.check, self.result, self.verbose)


class Cve(Base):
    __tablename__ = 'cve'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", back_populates="cves")

    def __repr__(self):
       return "<Status(name='%s')>" % (self.name)


class Defconfig(Base):
    __tablename__ = 'defconfig'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    path = Column(String)
    developers = relationship('Developer', secondary='link_defconfig_developer')

    def __repr__(self):
       return "<Defconfig(name='%s')>" % (self.name)


def _get_date():
    return datetime.date.today()


class Statistic(Base):
    __tablename__ = 'statistic'

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    packages = Column(Integer)
    outdated = Column(Integer)
