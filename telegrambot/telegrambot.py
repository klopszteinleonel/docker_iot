from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, asyncio, aiomysql, ssl
import matplotlib.pyplot as plt
from io import BytesIO
import aiomqtt

token = os.environ["TB_TOKEN"]

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- HELPER MQTT ---
async def mandar_comando_mqtt(mac_id, topico_final, payload=""):
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    try:
        async with aiomqtt.Client(
            os.environ["SERVIDOR"],
            username=os.environ.get("MQTT_USR"),
            password=os.environ.get("MQTT_PASS"),
            port=int(os.environ.get("PUERTO_MQTTS", 8883)),
            tls_context=tls_context,
        ) as client:
            topico = f"{mac_id}/{topico_final}"
            await client.publish(topico, payload, qos=1)
            logging.info(f"MQTT Publicado -> {topico}: {payload}")
            return True
    except Exception as e:
        logging.error(f"Error MQTT: {e}")
        return False

# --- HANDLERS DE COMANDOS MQTT ---
async def cmd_setpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /setpoint <MAC> <valor>")
        return
    mac = context.args[0]
    valor = context.args[1]
    exito = await mandar_comando_mqtt(mac, 'setpoint', valor)
    texto = f"Setpoint configurado en {valor} para {mac}" if exito else "Fallo al enviar comando MQTT."
    await update.message.reply_text(texto)

async def cmd_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /periodo <MAC> <segundos>")
        return
    mac = context.args[0]
    valor = context.args[1]
    exito = await mandar_comando_mqtt(mac, 'periodo', valor)
    texto = f"Período configurado en {valor}s para {mac}" if exito else "Fallo al enviar comando MQTT."
    await update.message.reply_text(texto)

async def cmd_modo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or context.args[1].upper() not in ['AUTO', 'MAN']:
        await update.message.reply_text("Uso: /modo <MAC> AUTO o /modo <MAC> MAN")
        return
    mac = context.args[0]
    modo = context.args[1].upper()
    exito = await mandar_comando_mqtt(mac, 'modo', modo)
    texto = f"Modo cambiado a {modo} para {mac}" if exito else "Fallo al enviar comando MQTT."
    await update.message.reply_text(texto)

async def cmd_rele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /rele <MAC>")
        return
    mac = context.args[0]
    exito = await mandar_comando_mqtt(mac, 'rele', 'toggle')
    texto = f"Comando de relé enviado a {mac} (solo funciona en MAN)." if exito else "Fallo al enviar comando MQTT."
    await update.message.reply_text(texto)

async def cmd_destello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /destello <MAC>")
        return
    mac = context.args[0]
    exito = await mandar_comando_mqtt(mac, 'destello', '1')
    texto = f"Destello activado en {mac}." if exito else "Fallo al enviar comando MQTT."
    await update.message.reply_text(texto)

# --- HANDLERS ORIGINALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre=update.message.from_user.first_name
    else:
        nombre=""
    if update.message.from_user.last_name:
        apellido=update.message.from_user.last_name
    else:
        apellido=""
    
    kb = [["setpoint", "periodo", "modo"], ["rele", "destello"]]
    await context.bot.send_message(update.message.chat.id, text=f"Bienvenido al Bot {nombre} {apellido}", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def acercade(update: Update, context):
    await context.bot.send_message(update.message.chat.id, text="Este bot fue creado para el curso de IoT FIO")

async def kill(update: Update, context):
    logging.info(context.args)
    if context.args and context.args[0] == '@e':
        await context.bot.send_animation(update.message.chat.id, "CgACAgQAAxkBAAMIahiDNVZQ9KWbP_zQlPxEMZ-n0e8AAu4FAAKXKVxS8yEdEF__M-c7BA")
        await asyncio.sleep(2)
        await context.bot.send_message(update.message.chat.id, text="Alo alo")
    else:
        await context.bot.send_message(update.message.chat.id, text="☠️ ¡¡¡Esto es muy peligroso!!! ☠️")


def main():
    application = Application.builder().token(token).build()
    
    # Comandos base
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('acercade', acercade))
    application.add_handler(CommandHandler('kill', kill))
    
    # Comandos MQTT
    application.add_handler(MessageHandler('setpoint', cmd_setpoint))
    application.add_handler(MessageHandler('periodo', cmd_periodo))
    application.add_handler(MessageHandler('modo', cmd_modo))
    application.add_handler(MessageHandler('rele', cmd_rele))
    application.add_handler(MessageHandler('destello', cmd_destello))
    
    application.run_polling()

if __name__ == '__main__':
    main()
