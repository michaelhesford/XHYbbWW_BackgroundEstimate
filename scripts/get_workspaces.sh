#!/bin/bash

tarballs=`eosls /store/user/mhesford/XHYbbWW_semileptonic/workspaces`

for tarball in $tarballs; do
    # Check if directory exists 
    IFS="." read -ra name <<< "$tarball"
    if [ ! -d $name ]; then 
        echo "Copying and unpacking ${tarball}"
        xrdcp "root://cmseosmgm01.fnal.gov:1094//store/user/mhesford/XHYbbWW_semileptonic/workspaces/${tarball}" .
        tar xzvf $tarball
        rm $tarball
    else
        echo "Directory ${name} exists - skipping."
    fi
done
