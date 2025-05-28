# Works in zsh, requires bash 4 or higher, which is not the default version on macOS
# find your shell with: echo $SHELL
# leave out #!/bin/bash

# Prepare environment

# Set environment variables
source .env
#printenv

### Clean out Solace ###

### Clean out MongoDB ###
# Atlas
#mongosh "$MONGODB_ATLAS_PROTOCOL$MONGODB_ATLAS_USERNAME$MONGODB_ATLAS_SEP$MONGODB_ATLAS_PASSWORD$MONGODB_ATLAS_SERVER" --eval "db.getSiblingDB('$MONGODB_ATLAS_DB_NAME').dropDatabase()"
# Local
#mongosh "mongodb://localhost:27017/" --eval "db.getSiblingDB('$MONGODB_ATLAS_DB_NAME').dropDatabase()"

### Clean out Neo4j ###
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
echo "removed transactions files"
rm -rf ./transactions/*.json
mkdir -p ./transactions && touch ./transactions/.empty
echo "removed output files"
rm -rf ./output/**
mkdir -p ./output && touch ./output/.empty
