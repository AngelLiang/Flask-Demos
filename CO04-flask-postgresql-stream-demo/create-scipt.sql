-- message表
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    channel INTEGER NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL
);

-- notify_on_insert 函数
CREATE OR REPLACE FUNCTION notify_on_insert() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('channel_' || NEW.channel,
        CAST(row_to_json(NEW) AS TEXT));
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- notify_on_insert 的触发器
CREATE TRIGGER notify_on_message_insert AFTER INSERT ON message
FOR EACH ROW EXECUTE PROCEDURE notify_on_insert();
