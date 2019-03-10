#!/usr/bin/env python
from __future__ import print_function
import hashlib

# file is sync
import requests
import os.path

from utils import login, get, create_url
import os
DIR="work_files"

class File(object):
    def __init__(self, dnac, name, namespace, path):
        self.dnac = dnac
        self.name = name
        self.namespace = namespace
        self.path = path + "/" + name
        self.fileid = None
        self.sha1 = None

    def update(self):
        try:
            f = open(self.path, "r")
            files = {'fileUpload': f}
        except:
            raise ValueError("Could not open file %s" % self.path)

        url = create_url(path="file/config/{}".format(self.fileid))
        headers = {'x-auth-token': self.dnac['token']}
        file_result = requests.put(url, files=files, headers=headers, verify=False)
        print(file_result.json())
        return file_result.json()

    def upload(self):
        try:
            f = open(self.path, "r")
            files = {'fileUpload': f}
        except:
            raise ValueError("Could not open file %s" % self.path)

        url = create_url(path="file/config")

        print("POST %s" % url)
        headers = {'x-auth-token': self.dnac['token']}

        try:
            response = requests.post(url, files=files, headers=headers, verify=False)
        except requests.exceptions.RequestException  as cerror:
            print("Error processing request", cerror)

        return(response.json())

    def delete(self):
        file_result = self.dnac.deleteFile(fileId=self.fileid)
        return file_result

    def present(self):
        files = get(self.dnac, "dna/intent/api/v1/file/namespace/{nameSpace}".format(nameSpace=self.namespace))
        fileid_list = [(file['id'], file['sha1Checksum']) for file in files.json()['response'] if file['name'] == self.name]
        self.fileid =  None if fileid_list == [] else fileid_list[0][0]
        self.sha1 = None if fileid_list == [] else fileid_list[0][1]
        return self.fileid


def check_namespace(apic, namespace):
    names = apic.file.getNameSpaceList()
    if names is not None:
        return namespace in names.response
    else:
        return False

def get_sha1(file):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return(hasher.hexdigest())

def process_namespace(dnac, namespace):

    # fix for windows
    #rootDir = DIR + "/" + namespace + "s"
    rootDir = os.path.join(DIR, namespace + "s")

    if not os.path.isdir(rootDir):
        print("No directory for {rootDir}, skipping".format(rootDir=rootDir))
        return

    for filename in os.listdir(rootDir):
        f = File(dnac, filename, namespace, rootDir)

        if f.present() is None:
            result = f.upload()
            print("Uploaded File:{file} ({id})".format(file=result['response']['name'],id=result['response']['id']))
        else:
            # need to look at checksum to see if need to update
            # fix for windows
            #sha1 = get_sha1(rootDir+ '/' + filename)
            sha1 = get_sha1(os.path.join(rootDir,filename))

            #print (filename, sha1, f.sha1)
            if sha1 != f.sha1:
                result = f.update()
                print("Updated File:{file} ({id})".format(file=result['response']['name'], id=result['response']['id']))
            else:
                print ("Skipping File:{file} ({id}) SHA1hash:{sha1}".format(file=filename, id=f.fileid, sha1=sha1))

def main():
    dnac = login()
    process_namespace(dnac,"config")
    print()

if __name__ == "__main__":
    main()