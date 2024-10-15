import socket
import time
import threading

def main():
    server_thread = threading.Thread(target=servidor)
    server_thread.start()

    while True:
        print("\nSistema Distribuido")
        print("-----------------------------------------")
        print("Lista de opciones:")
        print("1.Conexion\n2.Conversacion\n3.Salir")
        print("-----------------------------------------")

        opc = input("\nElija la opcion a realizar:")

        if opc == '1':
            instruccion_datos(coneccion())
        elif opc == '2':
            print("\nConecciones")
            print_history()
        elif opc == '3':
            break
        else:
            print("\nError")

def coneccion():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            return ip_address
    except Exception as e:
        print("Se ha detectado un error:", e)
        return None

def servidor():
    try:
        with open("catalogo.txt", "r") as file:
            server_info = [line.strip().split() for line in file.readlines() if line.strip().split()[0] == coneccion()]

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
                connection_time = time.strftime('%Y/%m/%d %H:%M:%S')
                print(f"\nConexion: {client_address} \nTiempo: {connection_time}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
    except Exception as e:
        print("\nError", e)

def instruccion_datos(local_ipv4):
    try:
        with open("catalogo.txt", "r") as file:
            remote_servers = [line.strip().split() for line in file.readlines() if not line.strip().split()[0] == local_ipv4]
        for i, (ip, port) in enumerate(remote_servers, 1):
            print(f"{i} : dir {ip} puerto {port}")
        choice = int(input("\nElija con quien desea la coneccion:"))
        if 1 <= choice <= len(remote_servers):
            remote_address, port = remote_servers[choice - 1]
            port = int(port)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((remote_address, port))
                print("Direccion IP conectada:", remote_address, "\nPuerto ", port)
                while True:
                    message = input("\nDesea enviar un dato (0 si desea salir):")
                    if message.lower() == '0':
                        break
                    message_with_timestamp = f"[{time.strftime('%Y/%m/%d %H:%M:%S')}] {message}"
                    client_socket.sendall(message_with_timestamp.encode())
                    save_message(local_ipv4, message_with_timestamp)
                    response = client_socket.recv(1024)
                    print("\n", response.decode())
        else:
            print("Error")
    except Exception as e:
        print("Error, no se conecta", e)

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print("Dato entrante", data.decode())
            if '[' in data.decode() and ']' in data.decode():
                timestamp = data.decode().split('[')[1].split(']')[0]
                print("Timestamp:", timestamp)
            save_message(client_socket.getpeername()[0], data.decode())
            if data.decode().strip().lower() == '0':
                break
            client_socket.sendall("Dato recibido".encode())
    except Exception as e:
        print("Error", e)
    finally:
        client_socket.close()
        print("Fin")

def save_message(ip_address, message):
    with open("almacena.txt", "a") as file:
        file.write(f"Datos: {message}, Dir IP: {ip_address}, Timestamp: {time.strftime('%Y/%m/%d %H:%M:%S')}\n")

def print_history():
    try:
        with open("almacena.txt", "r") as file:
            print(file.read())
    except FileNotFoundError:
        print("VACIO")

main()
