# Works in zsh, requires bash 4 or higher, which is not the default version on macOS
# find your shell with: echo $SHELL
# leave out #!/bin/bash

# Prepare environment
# Check file .env exists else exit
if [ ! -f .env ]; then
    echo "File .env not found!" >&2
    exit 1
fi
# Set environment variables
source .env
#printenv

### Clean out Solace ###

# TODO: remove all created queues, or just remove and restart docker container
echo "Remove Solace event broker docker container $SOLACE_NAME"
docker rm -f $SOLACE_NAME
echo "Create Solace event broker docker container $SOLACE_NAME"
# NOTE: chaining commands on success, not sure if this waits until broker is up and accessible... Otherwise use sleep
docker run -d -p 8080:8080 -p 55554:55555 -p 8008:8008 -p 1883:1883 -p 8000:8000 -p 5672:5672 -p 9000:9000 -p 2222:2222 --shm-size=2g --env username_admin_globalaccesslevel=$SOLACE_USER --env username_admin_password=$SOLACE_PASS --name=$SOLACE_NAME solace/solace-pubsub-standard
echo "Configure Solace event broker"
#todo: must use check like while not responsive sleep 1
sleep 10 #
python3 ez_broker_configuration.py

### Clean out MongoDB ###
# Atlas
#mongosh "$MONGODB_ATLAS_PROTOCOL$MONGODB_ATLAS_USERNAME$MONGODB_ATLAS_SEP$MONGODB_ATLAS_PASSWORD$MONGODB_ATLAS_SERVER" --eval "db.getSiblingDB('$MONGODB_ATLAS_DB_NAME').dropDatabase()"
# Local
#mongosh "mongodb://localhost:27017/" --eval "db.getSiblingDB('$MONGODB_ATLAS_DB_NAME').dropDatabase()"

echo "Clean out Neo4j"
# Delete all nodes and relationships
# Aura
#cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" "MATCH (n) DETACH DELETE n; CALL db.clearQueryCaches();"
# Local
cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI "MATCH (n) DETACH DELETE n; CALL db.clearQueryCaches();"
# Drop all indexes correctly (ensuring backticks)
indexes=$(cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI "SHOW INDEXES YIELD name RETURN name;" | tail -n +2)
for index_name in $indexes; do
  cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI "DROP INDEX \`$index_name\` IF EXISTS;"
done
# Drop all constraints correctly (ensuring backticks)
constraints=$(cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI "SHOW CONSTRAINTS YIELD name RETURN name;" | tail -n +2)
for constraint_name in $constraints; do
  cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI "DROP CONSTRAINT \`$constraint_name\` IF EXISTS;"
done

# Remove
rm -rf ./transactions/*.json && echo "Removed transactions files"
mkdir -p ./transactions && touch ./transactions/.empty && echo "Recreated transactions folder"
rm -rf ./output/** && echo "Removed output files"
mkdir -p ./output && touch ./output/.empty && echo "Recreated output folder"
rm -f shared.db && echo "Removed SQLite databasde"
rm -f ezsam/solace_agent_mesh.log ezsam/trace_None_default.txt ezsam/trace_None_None.txt && echo "Removed ezsam log and trace files"
