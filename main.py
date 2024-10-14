import socket
import threading
import time
from getIP import get_ipv4

def main():
    # Obtener la dirección IPv4 del host
    ipv4 = get_ipv4()

    # Iniciar servidor en un hilo
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    while True:
        print("\nMenú:")
        print("1. Conectarse a un servidor remoto")
        print("2. Mostrar historial de mensajes")
        print("3. Salir")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            connect_to_remote_server(ipv4)
        elif choice == '2':
            print("\nHistorial de mensajes:")
            print_history()
        elif choice == '3':
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")

def start_server():
    try:
        # Leer la dirección IP y el puerto correspondiente desde el archivo
        with open("remote_servers.txt", "r") as file:
            server_info = [line.strip().split() for line in file.readlines() if line.strip().split()[0] == get_ipv4()]

        if server_info:
            ip, port = server_info[0]
            port = int(port)
        else:
            print("No se encontró la dirección IP del host en el archivo.")
            return

        # Crear un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Enlace del socket a la dirección y el puerto
            server_socket.bind((ip, port))
            # Escuchar conexiones entrantes
            server_socket.listen(5)
            print(f"Servidor escuchando en {ip} en el puerto {port}")
            # Aceptar conexiones entrantes en un bucle infinito
            while True:
                client_socket, client_address = server_socket.accept()
                connection_time = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"Conexión entrante de {client_address} a las {connection_time}")
                # Manejar la conexión del cliente en un hilo separado
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
    except Exception as e:
        print("Error al iniciar el servidor:", e)


def connect_to_remote_server(local_ipv4):
    try:
        # Leer las direcciones IP y puertos desde el archivo
        with open("remote_servers.txt", "r") as file:
            remote_servers = [line.strip().split() for line in file.readlines() if not line.strip().split()[0] == local_ipv4]

        print("\nSeleccione el servidor remoto:")
        for i, (ip, port) in enumerate(remote_servers, 1):
            print(f"{i}. {ip}:{port}")

        choice = int(input("Seleccione una opción: "))
        if 1 <= choice <= len(remote_servers):
            remote_address, port = remote_servers[choice - 1]
            port = int(port)

            # Crear un socket TCP/IP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                # Conectar el socket al servidor remoto
                client_socket.connect((remote_address, port))
                print("Conexión establecida con el servidor remoto en", remote_address, "en el puerto", port)
                # Enviar mensajes al servidor remoto
                while True:
                    message = input("Introduce un mensaje para enviar al servidor remoto (o 'exit' para salir): ")
                    if message.lower() == 'exit':
                        break
                    message_with_timestamp = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
                    client_socket.sendall(message_with_timestamp.encode())
                    # Guardar el mensaje enviado en el archivo de texto
                    save_message("localhost", message_with_timestamp)
                    # Recibir la respuesta del servidor remoto
                    response = client_socket.recv(1024)
                    print("Respuesta del servidor remoto:", response.decode())
        else:
            print("Opción inválida.")
    except Exception as e:
        print("Error al conectar con el servidor remoto:", e)

def handle_client(client_socket):
    try:
        while True:
            # Recibir datos del cliente
            data = client_socket.recv(1024)
            if not data:
                break
            # Imprimir el mensaje recibido del cliente
            print("Mensaje recibido del cliente:", data.decode())
            # Si el mensaje contiene un timestamp, imprímelo
            if '[' in data.decode() and ']' in data.decode():
                timestamp = data.decode().split('[')[1].split(']')[0]
                print("Timestamp del mensaje:", timestamp)
            # Guardar el mensaje recibido en el archivo de texto
            save_message(client_socket.getpeername()[0], data.decode())
            # Si el cliente envía 'exit', salir del bucle y cerrar la conexión
            if data.decode().strip().lower() == 'exit':
                break
            # Enviar de vuelta el mensaje al cliente (eco)
            client_socket.sendall("Mensaje recibido".encode())
    except Exception as e:
        print("Error al manejar la conexión del cliente:", e)
    finally:
        # Cerrar el socket del cliente
        client_socket.close()
        print("Conexión con el cliente cerrada.")

def save_message(ip_address, message):
    with open("messages.txt", "a") as file:
        file.write(f"IP: {ip_address}, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}, Mensaje: {message}\n")


def print_history():
    try:
        with open("messages.txt", "r") as file:
            print(file.read())
    except FileNotFoundError:
        print("No se encontró ningún historial de mensajes.")

if __name__ == "__main__":
    main()
