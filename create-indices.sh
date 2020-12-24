curl -XPUT 'http://127.0.0.1:9200/block'
curl -XPOST 'http://127.0.0.1:9200/block/_mapping' -H "Content-Type: application/json" -d '
{
    "properties": {
        "index": {
            "type": "keyword"
        },
        "timestamp": {"type": "date"},
        "prev_hash": {"type": "keyword"},
        "hash": {"type": "keyword"},
        "nonce": {"type": "integer"},
        "confirm": {"type": "integer"}
    }
}'

curl -XPUT 'http://127.0.0.1:9200/block_test'
curl -XPOST 'http://127.0.0.1:9200/block_test/_mapping' -H "Content-Type: application/json" -d '
{
    "properties": {
        "index": {
            "type": "keyword"
        },
        "timestamp": {"type": "date"},
        "prev_hash": {"type": "keyword"},
        "hash": {"type": "keyword"},
        "nonce": {"type": "integer"},
        "confirm": {"type": "integer"}
    }
}'

curl -XPUT 'http://127.0.0.1:9200/tx'
curl -XPOST 'http://127.0.0.1:9200/tx/_mapping' -H "Content-Type: application/json" -d '
{
    "properties": {
        "from_wallet": {
            "type": "keyword"
        },
        "to_wallet": {
            "type": "keyword"
        },
        "value": {"type": "double"},
        "block": {"type": "keyword"},
        "timestamp": {"type": "date"},
        "hash": {"type": "keyword"},
        "status": {"type": "boolean"},
        "confirm": {"type": "integer"},
        "raw_value": {"type": "double"},
        "blockchain_fee": {"type": "double"},
        "size": {"type": "integer"}
    }
}'

curl -XPUT 'http://127.0.0.1:9200/tx_test'
curl -XPOST 'http://127.0.0.1:9200/tx_test/_mapping' -H "Content-Type: application/json" -d '
{
    "properties": {
        "from_wallet": {
            "type": "keyword"
        },
        "to_wallet": {
            "type": "keyword"
        },
        "value": {"type": "double"},
        "block": {"type": "keyword"},
        "timestamp": {"type": "date"},
        "hash": {"type": "keyword"},
        "status": {"type": "boolean"},
        "confirm": {"type": "integer"},
        "raw_value": {"type": "double"},
        "blockchain_fee": {"type": "double"},
        "size": {"type": "integer"}
    }
}'
