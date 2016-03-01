--
-- File generated with SQLiteStudio v3.0.7 on Tue Mar 1 16:07:37 2016
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: virtualization
DROP TABLE IF EXISTS virtualization;

CREATE TABLE virtualization (
    id   INTEGER NOT NULL
                 PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
);


-- Table: users
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     NOT NULL,
    username STRING  NOT NULL ON CONFLICT IGNORE
                     UNIQUE ON CONFLICT ROLLBACK
);


-- Table: vnf_names
DROP TABLE IF EXISTS vnf_names;

CREATE TABLE vnf_names (
    id   INTEGER NOT NULL
                 PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
);


-- Table: cpu_makes
DROP TABLE IF EXISTS cpu_makes;

CREATE TABLE cpu_makes (
    id   INTEGER NOT NULL
                 PRIMARY KEY AUTOINCREMENT,
    make TEXT    NOT NULL
);


-- Table: cpu
DROP TABLE IF EXISTS cpu;

CREATE TABLE cpu (
    id    INTEGER NOT NULL
                  PRIMARY KEY AUTOINCREMENT,
    make  INTEGER NOT NULL
                  REFERENCES cpu_makes (id) ON DELETE CASCADE
                                            ON UPDATE CASCADE,
    model INTEGER NOT NULL
                  REFERENCES cpu_models (id) ON DELETE CASCADE
                                             ON UPDATE CASCADE,
    FOREIGN KEY (
        make
    )
    REFERENCES cpu_makes (id),
    FOREIGN KEY (
        model
    )
    REFERENCES cpu_models (id) 
);


-- Table: cpu_models
DROP TABLE IF EXISTS cpu_models;

CREATE TABLE cpu_models (
    id    INTEGER NOT NULL
                  PRIMARY KEY AUTOINCREMENT,
    model TEXT    NOT NULL
);


-- Table: nic_models
DROP TABLE IF EXISTS nic_models;

CREATE TABLE nic_models (
    id    INTEGER NOT NULL
                  PRIMARY KEY AUTOINCREMENT,
    model TEXT    NOT NULL
);


-- Table: traffic_packet_sizes
DROP TABLE IF EXISTS traffic_packet_sizes;

CREATE TABLE traffic_packet_sizes (
    id          INTEGER NOT NULL
                        PRIMARY KEY AUTOINCREMENT,
    packet_size INTEGER NOT NULL
);


-- Table: traffic_names
DROP TABLE IF EXISTS traffic_names;

CREATE TABLE traffic_names (
    id      INTEGER NOT NULL
                    PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL,
    comment TEXT
);


-- Table: nic_makes
DROP TABLE IF EXISTS nic_makes;

CREATE TABLE nic_makes (
    id   INTEGER NOT NULL
                 PRIMARY KEY AUTOINCREMENT,
    make TEXT    NOT NULL
);


-- Table: vnf_functions
DROP TABLE IF EXISTS vnf_functions;

CREATE TABLE vnf_functions (
    id       INTEGER NOT NULL
                     PRIMARY KEY AUTOINCREMENT,
    function TEXT    NOT NULL
);


-- Table: vnf
DROP TABLE IF EXISTS vnf;

CREATE TABLE vnf (
    id             INTEGER NOT NULL
                           PRIMARY KEY AUTOINCREMENT,
    name           INTEGER NOT NULL
                           REFERENCES vnf_names (id) ON DELETE CASCADE
                                                     ON UPDATE CASCADE,
    version        TEXT    NOT NULL
                           DEFAULT (0),
    function       INTEGER NOT NULL
                           REFERENCES vnf_functions (id) ON DELETE CASCADE
                                                         ON UPDATE CASCADE,
    driver         INTEGER NOT NULL
                           REFERENCES vnf_drivers (id) ON DELETE CASCADE
                                                       ON UPDATE CASCADE,
    driver_version TEXT    NOT NULL
                           DEFAULT (0),
    FOREIGN KEY (
        name
    )
    REFERENCES vnf_names (id),
    FOREIGN KEY (
        function
    )
    REFERENCES vnf_functions (id),
    FOREIGN KEY (
        driver
    )
    REFERENCES vnf_drivers (id) 
);


-- Table: nic
DROP TABLE IF EXISTS nic;

CREATE TABLE nic (
    id        INTEGER NOT NULL
                      PRIMARY KEY AUTOINCREMENT,
    make      INTEGER NOT NULL
                      REFERENCES nic_makes (id) ON DELETE CASCADE
                                                ON UPDATE CASCADE,
    model     INTEGER NOT NULL
                      REFERENCES nic_models (id) ON DELETE CASCADE
                                                 ON UPDATE CASCADE,
    port_type STRING,
    FOREIGN KEY (
        make
    )
    REFERENCES nic_makes (id),
    FOREIGN KEY (
        model
    )
    REFERENCES nic_models (id) 
);


-- Table: vnf_drivers
DROP TABLE IF EXISTS vnf_drivers;

CREATE TABLE vnf_drivers (
    id     INTEGER NOT NULL
                   PRIMARY KEY AUTOINCREMENT,
    driver TEXT    NOT NULL
);


-- Table: measurements
DROP TABLE IF EXISTS measurements;

CREATE TABLE measurements (
    id             INTEGER NOT NULL
                           PRIMARY KEY AUTOINCREMENT,
    ts             DOUBLE  NOT NULL,
    name           TEXT,
    cpu            INTEGER NOT NULL
                           REFERENCES cpu (id) ON DELETE CASCADE
                                               ON UPDATE CASCADE,
    nic            INTEGER NOT NULL
                           REFERENCES nic (id) ON DELETE CASCADE
                                               ON UPDATE CASCADE,
    virtualization INTEGER NOT NULL
                           REFERENCES virtualization (id) ON DELETE CASCADE
                                                          ON UPDATE CASCADE,
    vnf            INTEGER NOT NULL
                           REFERENCES vnf (id) ON DELETE CASCADE
                                               ON UPDATE CASCADE,
    traffic        INTEGER NOT NULL
                           REFERENCES traffic_names (id) ON DELETE CASCADE
                                                         ON UPDATE CASCADE,
    repetitions    INTEGER NOT NULL,
    duration       INTEGER NOT NULL,
    sent_pps_min   BIGINT  NOT NULL,
    sent_pps_avg   DOUBLE  NOT NULL,
    sent_pps_max   BIGINT  NOT NULL,
    recv_pps_min   BIGINT  NOT NULL,
    recv_pps_avg   DOUBLE  NOT NULL,
    recv_pps_max   BIGINT  NOT NULL,
    miss_pps_min   BIGINT  NOT NULL,
    miss_pps_avg   DOUBLE  NOT NULL,
    miss_pps_max   BIGINT  NOT NULL,
    sent_bps_min   BIGINT  NOT NULL,
    sent_bps_avg   DOUBLE  NOT NULL,
    sent_bps_max   BIGINT  NOT NULL,
    recv_bps_min   BIGINT  NOT NULL,
    recv_bps_avg   DOUBLE  NOT NULL,
    recv_bps_max   BIGINT  NOT NULL,
    diff_bps_min   BIGINT  NOT NULL,
    diff_bps_avg   DOUBLE  NOT NULL,
    diff_bps_max   BIGINT  NOT NULL,
    bidir_twin_id  INTEGER,
    comment        TEXT,
    user_id        INTEGER REFERENCES users (id) ON DELETE CASCADE
                                                 ON UPDATE CASCADE
                           NOT NULL,
    bidir          BOOLEAN NOT NULL
                           DEFAULT FALSE,
    FOREIGN KEY (
        cpu
    )
    REFERENCES cpu_makes (id),
    FOREIGN KEY (
        nic
    )
    REFERENCES nic (id),
    FOREIGN KEY (
        virtualization
    )
    REFERENCES virtualization (id),
    FOREIGN KEY (
        vnf
    )
    REFERENCES vnf (id),
    FOREIGN KEY (
        traffic
    )
    REFERENCES traffic_names (id) 
);


-- Table: traffic
DROP TABLE IF EXISTS traffic;

CREATE TABLE traffic (
    id          INTEGER NOT NULL
                        PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL
                        REFERENCES traffic_names (id) ON DELETE CASCADE
                                                      ON UPDATE CASCADE,
    packet_size INTEGER NOT NULL
                        REFERENCES traffic_packet_sizes (id) ON DELETE CASCADE
                                                             ON UPDATE CASCADE,
    FOREIGN KEY (
        name
    )
    REFERENCES traffic_names (id),
    FOREIGN KEY (
        packet_size
    )
    REFERENCES traffic_packet_sizes (id) 
);


-- View: vnf_view
DROP VIEW IF EXISTS vnf_view;
CREATE VIEW vnf_view AS
    SELECT vnf.id,
           vnf_names.name,
           vnf.version,
           vnf_functions.function,
           vnf_drivers.driver,
           vnf.driver_version
      FROM vnf
           JOIN
           vnf_names ON vnf.name = vnf_names.id
           JOIN
           vnf_functions ON vnf.function = vnf_functions.id
           JOIN
           vnf_drivers ON vnf.driver = vnf_drivers.id;



-- View: traffic_view
DROP VIEW IF EXISTS traffic_view;
CREATE VIEW traffic_view AS
    SELECT traffic.id,
           traffic_names.name,
           traffic_packet_sizes.packet_size,
           traffic_names.comment
      FROM traffic
           JOIN
           traffic_names ON traffic.name = traffic_names.id
           JOIN
           traffic_packet_sizes ON traffic.packet_size = traffic_packet_sizes.id;


-- View: nic_view
DROP VIEW IF EXISTS nic_view;
CREATE VIEW nic_view AS
    SELECT nic.id,
           nic_makes.make,
           nic_models.model,
           nic.port_type
      FROM nic
           JOIN
           nic_makes ON nic.make = nic_makes.id
           JOIN
           nic_models ON nic.model = nic_models.id;


-- View: cpu_view
DROP VIEW IF EXISTS cpu_view;
CREATE VIEW cpu_view AS
    SELECT cpu.id,
           cpu_makes.make,
           cpu_models.model
      FROM cpu
           JOIN
           cpu_makes ON cpu.make = cpu_makes.id
           JOIN
           cpu_models ON cpu.model = cpu_models.id;


-- View: measurements_view
DROP VIEW IF EXISTS measurements_view;
CREATE VIEW measurements_view AS
    SELECT measurements.id,
           measurements.name,
           datetime(measurements.ts) AS to_timestamp,
           cpu_view.make AS cpu_make,
           cpu_view.model AS cpu_model,
           nic_view.make AS nic_make,
           nic_view.model AS nic_model,
           virtualization.name AS virtualization,
           vnf_view.name AS vnf_name,
           vnf_view.version AS vnf_version,
           vnf_view.function AS vnf_functions,
           vnf_view.driver AS vnf_driver,
           vnf_view.driver_version AS vnf_driver_version,
           traffic_view.name AS traffic_name,
           traffic_view.packet_size AS traffic_packet_size,
           measurements.repetitions,
           measurements.duration,
           measurements.sent_pps_min,
           measurements.sent_pps_avg,
           measurements.sent_pps_max,
           measurements.recv_pps_min,
           measurements.recv_pps_avg,
           measurements.recv_pps_max,
           measurements.miss_pps_min,
           measurements.miss_pps_avg,
           measurements.miss_pps_max,
           measurements.sent_bps_min,
           measurements.sent_bps_avg,
           measurements.sent_bps_max,
           measurements.recv_bps_min,
           measurements.recv_bps_avg,
           measurements.recv_bps_max,
           measurements.diff_bps_min,
           measurements.diff_bps_avg,
           measurements.diff_bps_max,
           measurements.bidir,
           measurements.bidir_twin_id,
           measurements.comment,
           users.username
      FROM measurements
           JOIN
           cpu_view ON measurements.cpu = cpu_view.id
           JOIN
           nic_view ON measurements.nic = nic_view.id
           JOIN
           virtualization ON measurements.virtualization = virtualization.id
           JOIN
           vnf_view ON measurements.vnf = vnf_view.id
           JOIN
           traffic_view ON measurements.traffic = traffic_view.id
           JOIN
           users ON measurements.user_id = users.id
     ORDER BY measurements.id;


-- View: measurements_view_v2
DROP VIEW IF EXISTS measurements_view_v2;
CREATE VIEW measurements_view_v2 AS
    SELECT measurements.id,
           measurements.name,
           traffic_view.name AS traffic_name,
           traffic_view.packet_size AS traffic_packet_size,
           measurements.recv_pps_avg,
           measurements.recv_bps_avg,
           measurements.bidir,
           measurements.bidir_twin_id,
           measurements.comment,
           cpu_view.make AS cpu_make,
           cpu_view.model AS cpu_model,
           nic_view.make AS nic_make,
           nic_view.model AS nic_model,
           virtualization.name AS virtualization,
           vnf_view.name AS vnf_name,
           vnf_view.version AS vnf_version,
           vnf_view.function AS vnf_functions,
           vnf_view.driver AS vnf_driver,
           vnf_view.driver_version AS vnf_driver_version
      FROM measurements
           JOIN
           cpu_view ON measurements.cpu = cpu_view.id
           JOIN
           nic_view ON measurements.nic = nic_view.id
           JOIN
           virtualization ON measurements.virtualization = virtualization.id
           JOIN
           vnf_view ON measurements.vnf = vnf_view.id
           JOIN
           traffic_view ON measurements.traffic = traffic_view.id
           JOIN
           users ON measurements.user_id = users.id
     ORDER BY measurements.name,
              traffic_name,
              traffic_packet_size;



COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
