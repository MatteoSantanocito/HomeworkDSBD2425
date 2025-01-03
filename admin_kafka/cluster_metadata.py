from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException
import time 
import topic_creation 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_metadata():
    """Recupera e stampa i metadati del cluster Kafka."""
    admin_client = AdminClient({'bootstrap.servers': ','.join(topic_creation.bootstrap_servers)})
    try:
        logger.info("Recupero dei metadati dal cluster Kafka...")
        metadata = admin_client.list_topics(timeout=10)

        if not metadata.brokers:
            logger.warning("Nessun broker trovato nel cluster.")
            return
        
        logger.info("Broker nel cluster Kafka:")
        for broker in metadata.brokers.values():
            logger.info(f"Broker ID: {broker.id}, Host: {broker.host}, Porta: {broker.port}")

        if not metadata.topics:
            logger.warning("Nessun topic trovato nel cluster.")
            return

        logger.info("Topic e partizioni nel cluster Kafka:")
        for topic, topic_metadata in metadata.topics.items():
            logger.info(f"Topic: {topic}")
            if topic_metadata.error:
                logger.error(f"Errore per il topic '{topic}': {topic_metadata.error}")
            else:
                for partition_id, partition_metadata in topic_metadata.partitions.items():
                    leader = partition_metadata.leader
                    replicas = partition_metadata.replicas
                    isrs = partition_metadata.isrs
                    logger.info(f"  Partizione {partition_id}:")
                    logger.info(f"  Leader: Broker {leader}")
                    logger.info(f"  Repliche: {replicas}")
                    logger.info(f"  Repliche In-Sync (ISR): {isrs}")

    except KafkaException as e:
        logger.error(f"Errore durante il recupero dei metadati: {e}")
    except Exception as e:
        logger.exception(f"Errore imprevisto durante il recupero dei metadati: {e}")
    finally:
        logger.info("Operazione di recupero metadati completata.")
        
        

if __name__ == "__main__":
    
    time.sleep(30)
    
    try:
        logger.info("Se non esistono topic, li sto creando\n")
        topic_creation.create_topic_if_not_exists(topic_creation.topic_list, num_partitions=topic_creation.num_partitions, replication_factor=topic_creation.replication_factor)
        topic_creation.list_topics_and_details()        
    except Exception as e:
        logger.error(f"Errore: {e}")
        exit(1)

    while True:
        time.sleep(120)
        get_metadata()