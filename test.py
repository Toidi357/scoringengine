import smbclient
share = 'share'
credentials = 'SIXSEVEN\\scoring:Pa$$w0rd10'
file = 'images.jpg'


username, password = credentials.split(":")



smbclient.register_session('192.168.100.30', username=username, password=password, connection_timeout=10)

dir_contents = smbclient.listdir(f"\\\\192.168.100.30\\{share}")

print(type(dir_contents))
