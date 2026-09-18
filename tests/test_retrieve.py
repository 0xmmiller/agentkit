from agentkit.retrieve import retrieve


def test_retrieve_cites_kafka_adr():
    hits = retrieve("why kafka not nats", k=2)
    assert hits[0]["path"] == "adr/001-message-broker.md"
    assert hits[0]["score"] > 0
