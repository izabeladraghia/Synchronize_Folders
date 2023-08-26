import os
import shutil
import argparse
import time
import hashlib

#Calculate MD5 for file
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

#Log message to log file
def log_to_file_and_console(message, log_file_path):
    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')
    print(message)

#Synchronize the 2 folders
def synchronize_folders(source, replica, log_file_path):
    source_files = set(os.listdir(source))
    replica_files = set(os.listdir(replica))

#Files that are only in the source
    only_in_source = source_files - replica_files
    for file in only_in_source:
        source_path = os.path.join(source, file)
        replica_path = os.path.join(replica, file)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, replica_path)
            log_to_file_and_console(f"Copied directory {source_path} to {replica_path}", log_file_path)
        else:
            shutil.copy2(source_path, replica_path)
            log_to_file_and_console(f"Copied file {source_path} to {replica_path}", log_file_path)

#Files that are only in the replica
    only_in_replica = replica_files - source_files
    for file in only_in_replica:
        replica_path = os.path.join(replica, file)
        if os.path.isdir(replica_path):
            shutil.rmtree(replica_path)
            log_to_file_and_console(f"Removed directory {replica_path}", log_file_path)
        else:
            os.remove(replica_path)
            log_to_file_and_console(f"Removed file {replica_path}", log_file_path)

#Check for modified files in the common set
    for common_file in source_files & replica_files:
        source_path = os.path.join(source, common_file)
        replica_path = os.path.join(replica, common_file)
        if os.path.isfile(source_path) and os.path.isfile(replica_path):
            if calculate_md5(source_path) != calculate_md5(replica_path):
                shutil.copy2(source_path, replica_path)
                log_to_file_and_console(f"Updated file {source_path} in replica", log_file_path)

def main():
#Set requiredn info
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('source', help='Path to the source folder.')
    parser.add_argument('replica', help='Path to the replica folder.')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds.')
    parser.add_argument('log_file_path', help='Path to the log file.')

    args = parser.parse_args()

    while True:
#Synchronize folders
        synchronize_folders(args.source, args.replica, args.log_file_path)
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
