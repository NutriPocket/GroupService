-- Connect to the default 'postgres' database
\c postgres;

-- Check if the database exists, if not, create it
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'database') THEN
      CREATE DATABASE database;
   END IF;
END
$do$;

-- Connect to the newly created database
\c database

\i src/sql/tables.sql;
