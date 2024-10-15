import socket
import time
import threading

from getIP import get_ipv4

def main():
    ipv4 = get_ipv4()
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    while True:
        print("\nSistema Distribuido")
        print("-----------------------------------------")
        print("\nLista de opciones:")
        print("1.Conexion\n2.Conversacion\n3.Salir")
        print("-----------------------------------------")

        opc = input("\nElija la opcion a realizar: ")

        if opc == '1':
            connect_to_remote_server(ipv4)
        elif opc == '2':
            print("\nConecciones:")
            print_history()
        elif opc == '3':
            print(" ")
            break
        else:
            print("\nError")

def start_server():
    try:
        with open("ip.txt", "r") as file:
            server_info = [line.strip().split() for line in file.readlines() if line.strip().split()[0] == get_ipv4()]

        if server_info:
            ip, port = server_info[0]
            port = int(port)
        else:
            print("IP denegada")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((ip, port))
            server_socket.listen(5)
            while True:
                client_socket, client_address = server_socket.accept()
                connection_time = time.strftime('%Y-%m-%d %H:%M:%S')
                print("\nDireccion: {client_address} \nTiempo: {connection_time}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
    except Exception as e:
        print("\nError", e)


def connect_to_remote_server(local_ipv4):
    try:
        with open("ip.txt", "r") as file:
            ip = [line.strip().split() for line in file.readlines() if not line.strip().split()[0] == local_ipv4]

        print("\nElija la direccion a la que desee entrar:")
        for i, (ip, port) in enumerate(ip, 1):
            print("{i}. {ip}:{port}")

        opc = int(input("\nNumero de direccion: "))
        if 1 <= opc <= len(ip):
            remote_address, port = ip[opc - 1]
            port = int(port)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((remote_address, port))
                print("Conexion con", remote_address, "del puerto", port)

                while True:
                    message = input("\nMensaje\n(pon 0 para salir): ")
                    if message.lower() == '0' :
                        break
                    message_with_timestamp = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
                    client_socket.sendall(message_with_timestamp.encode())
                    save_message("localhost", message_with_timestamp)
                    response = client_socket.recv(1024)
                    print("Respuesta:", response.decode())
        else:
            print("/nError")
    except Exception as e:
        print("/nError en e", e)
        
def handle_client(client_socket):
    try:
        while True:

            data = client_socket.recv(1024)
            if not data:
                break
            print("Mensaje recibido del cliente:", data.decode())
            if '[' in data.decode() and ']' in data.decode():
                timestamp = data.decode().split('[')[1].split(']')[0]
                print("Timestamp del mensaje:", timestamp)
            save_message(client_socket.getpeername()[0], data.decode())
            if data.decode().strip().lower() == '0' :
                break
            # Enviar de vuelta el mensaje al cliente (eco)
            client_socket.sendall("Mensaje recibido".encode())
    except Exception as e:
        print("/nError", e)
    finally:
        client_socket.close()
        print("Conexion con el cliente cerrada.")

def save_message(ip_address, message):
    with open("Almacen.txt", "a") as file:
        file.write(f"IP: {ip_address}, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}, Mensaje: {message}\n")


def print_history():
    try:
        with open("Almacen.txt", "r") as file:
            print(file.read())
    except FileNotFoundError:
        print("/nNo hay mensajes")

if __name__ == "__main__":
    main()

