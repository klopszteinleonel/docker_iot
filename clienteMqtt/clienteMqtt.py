import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(format='%(asctime)s - cliente mqtt - TASK:%(taskName)s - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S %z')
   
async def topico1(message):
    logging.info("Mensaje: " + str(message.topic) + ": " + message.payload.decode("utf-8"))

async def topico2(message):
    logging.info("Mensaje: " + str(message.topic) + ": " + message.payload.decode("utf-8"))

async def mensajes(client):
    async for message in client.messages:
        if(str(message.topic) == str(os.environ['TOPICO1'])):
            asyncio.create_task(topico1(message), name="topico1")
        elif(str(message.topic) == str(os.environ['TOPICO2'])):
            asyncio.create_task(topico2(message), name="topico2")

async def incrementar(contador, seg):
    while True:
        contador["estado"]+=1
        await asyncio.sleep(seg)

async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port=8883,
        tls_context=tls_context,
    ) as client:
        await client.subscribe(os.environ['TOPICO1'])
        await client.subscribe(os.environ['TOPICO2'])

        contador = {"estado": 0}
        asyncio.create_task(incrementar(contador, 3), name="incrementar")
        asyncio.create_task(mensajes(client), name="mensajes")

        while True:

            await client.publish(os.environ['TOPICO_PUB'], contador["estado"], qos=1)

            await asyncio.sleep(5)
        

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Programa detenido por el usuario (Ctrl+C)")
