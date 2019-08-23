# MovR

MovR is a fictional vehicle-sharing company. 

This repo contains the following:

- A SQLAlchemy mapping of the [MovR database](https://www.cockroachlabs.com/docs/dev/movr.html)
- A REST API to the MovR database mapping
- A web server that hosts an interactive web UI for MovR
- A fake data generator for the MovR database

For more information about MovR, see the [MovR webpage](https://www.cockroachlabs.com/docs/dev/movr.html).

## Getting started

### Set up a CockroachDB cluster

1. Download and install the [latest release](https://www.cockroachlabs.com/docs/releases/#testing-releases) of CockroachDB.

2. Run [`cockroach demo movr`](https://www.cockroachlabs.com/docs/dev/cockroach-demo.html) with the `--nodes` and `--demo-locality` tags. This command opens an interactive SQL shell to a temporary, multi-node in-memory cluster with the `movr` database preloaded and set as the [current database](https://www.cockroachlabs.com/docs/dev/sql-name-resolution.html#current-database):
    ~~~ shell
    $ cockroach demo movr --nodes=3 --demo-locality=region=us-east1,region=us-central1,region=us-west1
    ~~~

    **Note**: You can also [start a local cluster](https://www.cockroachlabs.com/docs/dev/start-a-local-cluster.html) and then use [`cockroach workload`](https://www.cockroachlabs.com/docs/dev/cockroach-workload.html#movr-workload) to load the `movr` database and dataset into the running cluster. Then you can open a SQL shell to the cluster with [`cockroach sql`](https://www.cockroachlabs.com/docs/dev/cockroach-sql.html)

### Start the web server

1. Set up your python development environment. 

    **Tip**: `virtualenv` is helpful for managing dependencies in a development environment, which are listed in [`requirements.txt`](/requirements.txt).

    ~~~ shell
    $ pip install virtualenv
    $ python -m venv my-env
    $ source my-env/bin/activate
    $ pip install -r requirements.txt
    ~~~

2. Start the web server:
    
    ~~~ shell
    $ python web-server.py
    ~~~
    ~~~
    * Serving Flask app "web-server" (lazy loading)
    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 
    ~~~
3. Direct your browser to http://127.0.0.1:5000/.

## Generating fake data

Generating fake data: `docker run -it --rm cockroachdb/movr --url "postgres://root@docker.for.mac.localhost:26257/movr?sslmode=disable" load --num-users 100 --num-rides 100 --num-vehicles 10`

Generating load for cities: `docker run -it --rm cockroachdb/movr --url "postgres://root@docker.for.mac.localhost:26257/movr?sslmode=disable" --num-threads 10 run --city "new york" --city "boston"`

## Partitioning MovR data

MovR can automatically partition data and apply zone configs using the `partition` command.
Use region-city pairs to map cities to regional partitions and use region-zone pairs to map regional partitions to zones
`docker run -it --rm cockroachdb/movr --echo-sql --app-name "movr-partition" --url "postgres://root@[ipaddress]/movr?sslmode=disable" partition --region-city-pair us_east:"new york" --region-city-pair central:chicago --region-city-pair us_west:seattle  --region-zone-pair us_east:us-east1 --region-zone-pair central:us-central1 --region-zone-pair us_west:us-west1`

If you want to partition by hand (perhaps in a demo), MovR can print the partition commands with the `--preview-queries` command. Example:
```
Partitioning Setting Summary

partition    city
-----------  --------
chicago      chicago
new_york     new york
seattle      seattle

partition    zone where partitioned data will be moved
-----------  -------------------------------------------
new_york     us-east1
chicago      us-central1
seattle      us-west1

reference table    zones where index data will be replicated
-----------------  -------------------------------------------
promo_codes        us-east1
promo_codes        us-central1
promo_codes        us-west1

queries to geo-partition the database
===table and index partitions===
ALTER TABLE vehicles PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
ALTER TABLE users PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
ALTER TABLE rides PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
```

## API

get vehicles: `curl http://localhost:3000/api/boston/vehicles.json`

add vehicle: `curl -d '{"owner_id":"15556084-a515-4f00-8000-000000014586", "type":"scooter", "vehicle_metadata":{"brand": "Kona", "color": "green"},"status":"available","current_location":"home"}' -H "Content-Type: application/json" -X PUT http://localhost:3000/api/vehicles/boston`

add ride_history: `curl -d '{"lat":10, "long": 14}' -H "Content-Type: application/json" -X PUT http://localhost:3000/api/rides/amsterdam/c0000000-0000-4000-8000-0000000b71b0/locations.json`


### MovR 1M

This dataset contains 1M users, 1M rides, and 10k vehicles.

Import Users
```
IMPORT TABLE users (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        name VARCHAR NULL,
        address VARCHAR NULL,
        credit_card VARCHAR NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        FAMILY "primary" (id, city, name, address, credit_card)
)
CSV DATA (
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.0.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.1.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.2.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.3.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.4.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.5.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.6.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.7.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.8.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.9.csv',
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.10.csv');

```

Import vehicles

```
IMPORT TABLE vehicles (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        type VARCHAR NULL,
        owner_id UUID NULL,
        creation_time TIMESTAMP NULL,
        status VARCHAR NULL,
        current_location VARCHAR NULL,
        ext JSONB NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        INDEX vehicles_auto_index_fk_city_ref_users (city ASC, owner_id ASC),
        INVERTED INDEX ix_vehicle_ext (ext),
        FAMILY "primary" (id, city, type, owner_id, creation_time, status, current_location, ext)
)                                                                                                                                                                
CSV DATA ('https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/vehicles/n1.0.csv');

```

Import rides

```
IMPORT TABLE rides (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        vehicle_city VARCHAR NULL,
        rider_id UUID NULL,
        vehicle_id UUID NULL,
        start_address VARCHAR NULL,
        end_address VARCHAR NULL,
        start_time TIMESTAMP NULL,
        end_time TIMESTAMP NULL,
        revenue DECIMAL(10,2) NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        INDEX rides_auto_index_fk_city_ref_users (city ASC, rider_id ASC),
        INDEX rides_auto_index_fk_vehicle_city_ref_vehicles (vehicle_city ASC, vehicle_id ASC),
        FAMILY "primary" (id, city, vehicle_city, rider_id, vehicle_id, start_address, end_address, start_time, end_time, revenue),
        CONSTRAINT check_vehicle_city_city CHECK (vehicle_city = city)
) 
CSV DATA (
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.0.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.1.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.2.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.3.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.4.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.5.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.6.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.7.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.8.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.9.csv',
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.10.csv');
```

Setup and validate integrity constraints

```
ALTER TABLE vehicles ADD CONSTRAINT fk_city_ref_users FOREIGN KEY (city, owner_id) REFERENCES users (city, id);
ALTER TABLE rides ADD CONSTRAINT fk_city_ref_users FOREIGN KEY (city, rider_id) REFERENCES users (city, id);
ALTER TABLE rides ADD CONSTRAINT fk_vehicle_city_ref_vehicles FOREIGN KEY (vehicle_city, vehicle_id) REFERENCES vehicles (city, id);

ALTER TABLE vehicles VALIDATE CONSTRAINT fk_city_ref_users;
ALTER TABLE rides VALIDATE CONSTRAINT fk_city_ref_users;
ALTER TABLE rides VALIDATE CONSTRAINT fk_vehicle_city_ref_vehicles;


```
