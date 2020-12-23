#!/bin/bash

set -e

if [ "$1" == "help" ] || [ "$1" == "-help" ] || [ "$1" == "--help" ]
then
    echo -e "\033[1;94m🌊 seaport 🌊\033[0m"
    echo -e "\033[0;36mA more mighty port bump\033[0m"
    echo -e "\nUsage:
        seaport help            Display this message
        seaport name            Bump the version and checksums for this port

        seaport name [version]
    "
    exit 0
fi

INSTALLDIR="$HOME/seaport"  # Where the cloned and local portfile repos are stored
REPO="macports/macports-ports"  # Where to send the PR to
CLONE=$(basename $REPO)  # Name of cloned folder e.g. macports-ports
NAME="$1"  # Port to update
NEW="$2"  # New version
CURRENT=$(port info --version "$NAME" | sed 's/[A-Za-z: ]*//g') # Remove letters, colon and space

# Only take the first category
# Replace commas with line breaks
CATEGORY=$(port info --category "$NAME")
CATEGORY=$(echo "$CATEGORY" | cut -d' ' -f2 | tr "," "\n")

if [ "$2" == "" ]
then
    # Take the last word of livecheck and remove the )
    NEW=$(port livecheck "$NAME" | sed 's/.* //g' | sed 's|)||g')
    echo "New version number is $NEW!"
fi

if [ ! -d "$INSTALLDIR" ]; then
    echo -e "\033[1;94m🔨 Creating installation directory\033[0m"
    echo "Location: $INSTALLDIR"
    mkdir -p "$INSTALLDIR"
fi

cd "$INSTALLDIR" || exit 1

if [ ! -d "ports" ]; then
    echo -e "\033[1;94m📁 Creating local Portfile Repo\033[0m"

    # Prefix credit to GiovanniBussi/macports-ci
    w=$(which port)
    MACPORTS_PREFIX="${w%/bin/port}"
    SOURCES=$MACPORTS_PREFIX/etc/macports/sources.conf

    mkdir sources
    cp "$SOURCES" "$INSTALLDIR"/sources/sources.conf
    cp "$SOURCES" "$INSTALLDIR"/sources/edit.conf

    # Make edits without sudo, and then move file back
    # Only two slashes needed since INSTALLDIR already has one
    echo -e "file://$INSTALLDIR/ports\n$(cat "$INSTALLDIR"/sources/edit.conf)" > "$INSTALLDIR"/sources/edit.conf

    echo -e "\033[0;31m🔑 Password required to add URL pointing to local repo location \033[0m"
    echo "Backup File made: $INSTALLDIR/sources/sources.conf"

    sudo cp -f "$INSTALLDIR"/sources/edit.conf "$SOURCES"

    mkdir -p "ports"
    portindex
fi

if [ ! -d "$CLONE" ]; then
    echo -e "\033[1;94m⬇️ Cloning $REPO\033[0m"
    echo "Location: $INSTALLDIR/$CLONE"
    gh repo fork "$REPO" "--clone=true" "--remote=true"
fi

echo -e "\033[1;94m⬆️ Updating origin\033[0m"

cd "$CLONE"
git fetch upstream
git merge upstream/master
git push
cd ..

echo -e "\033[1;94m⏫ Bumping Version\033[0m"

mkdir -p ports/"$CATEGORY"/"$NAME"
# Copy Portfile to the local repo
cp "$CLONE"/"$CATEGORY"/"$NAME"/Portfile ports/"$CATEGORY"/"$NAME"/Portfile

cd ports && portindex && cd ..

# Replaces first instance of old version with new version
sed -i '' "1,/$CURRENT/ s/$CURRENT/$NEW/" ports/"$CATEGORY"/"$NAME"/Portfile
sudo port bump "$NAME"

echo -e "\033[1;94m📨 Sending PR\033[0m"

cd "$CLONE"
git checkout -b "seaport-$NAME-$NEW"
# Copy changes back to main repo
cp ../ports/"$CATEGORY"/"$NAME"/Portfile "$CATEGORY"/"$NAME"/Portfile
git add "$CATEGORY"/"$NAME"/Portfile
git commit -m "$NAME: update to $NEW"
git config "remote.upstream.gh-resolved" "base"  # Automatically chose to send PR to remote
git push --set-upstream origin "seaport-$NAME-$NEW"
gh pr create --title "$NAME: update to $NEW" --body "Created with [seaport](https://github.com/harens/seaport)"

# Cleanup (remove changed ports)
git checkout master
git branch -D "seaport-$NAME-$NEW"
cd ..
rm -rf ports/"$CATEGORY"
cd ports && portindex
