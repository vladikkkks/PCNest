CREATE DATABASE pc_nest;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'pc_nest_user') THEN
      CREATE ROLE pc_nest_user LOGIN PASSWORD 'pc_nest_password';
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE pc_nest TO pc_nest_user;
