app_name="kamstrupd"

# determine controller's identity
host_name=$(hostname)


# construct database paths
database_filename="electriciteit.sqlite3"
database_path="/srv/databases"
db_full_path="${database_path}/${database_filename}"
