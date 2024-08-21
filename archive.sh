#! /bin/bash
set +x
VERSION=0.4.0

# cleanup

find . -type d -name __pycache__ | xargs rm -rf

# create archive

cd ..
tar \
    --exclude-vcs \
    --exclude=data \
    --exclude=debian \
    --exclude=.pc \
    --exclude=*~ \
    --exclude=pyproject.toml \
    --exclude=poetry.lock \
    -zcvf python-magnetgeo_$VERSION.orig.tar.gz python_magnetgeo

mkdir -p tmp
cd tmp
cp ../python-magnetgeo_$VERSION.orig.tar.gz .
tar zxvf ./python-magnetgeo_$VERSION.orig.tar.gz
cp -r ../python_magnetgeo/debian python_magnetgeo
cd python_magnetgeo
DIST=bookworm pdebuild

cd ..
rm -rf python-magnetgeo*
rm -rf python_magnetgeo