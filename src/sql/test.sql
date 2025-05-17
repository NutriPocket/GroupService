-- Connect to the default 'postgres' database
\c postgres;

DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test') THEN
      CREATE DATABASE test;
   END IF;
END
$do$;

-- Connect to the newly created database
\c test

\i src/sql/tables.sql;