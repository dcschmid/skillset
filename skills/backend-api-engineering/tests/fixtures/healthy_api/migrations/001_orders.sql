-- UP
CREATE TABLE orders (id integer primary key, owner_id int not null, tenant text not null,
                     total numeric not null, status text not null default 'new',
                     created_at text not null default (datetime('now')));
CREATE INDEX idx_orders_owner ON orders (tenant, owner_id, created_at);
-- DOWN
DROP TABLE orders;
