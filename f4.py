import openstack
import traceback

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFg-rHOrSC_9qdw2WjLyhyI3DoQwHLnf7PChV5yZoG4JxUQRO3QoXrG89l4fk9i8ddWbqH4ucP_5V_kEVCyelG_U5l0drfp2198L2o0LFyywwKJ97x1IPiFZIgh-5W6MFXuIkYNMR5Q8nVzy9oGvPREt1FtNDX8i7fMevcwR-fRvdsn0',
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def create_network(conn, network_name, subnet_cidr="192.168.0.0/24"):
    try:
        print(f"🌐 Creating network '{network_name}'...")
        network = conn.network.create_network(name=network_name)
        print(f"🔹 Network '{network_name}' created with ID: {network.id}")

        print(f"🌐 Creating subnet for network '{network_name}' with CIDR {subnet_cidr}...")
        subnet = conn.network.create_subnet(
            network_id=network.id,
            ip_version='4',
            cidr=subnet_cidr,
            name=f"{network_name}-subnet"
        )
        print(f"🔹 Subnet '{subnet.name}' created with ID: {subnet.id}")

        print(f"✅ Network '{network_name}' and subnet created successfully.")
        return network, subnet
    except Exception as e:
        print(f"❌ Failed to create network and subnet: {e}")
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    conn = connect_openstack()
    if conn:
        network_name = "blue-net"
        network, subnet = create_network(conn, network_name)
        if not network:
            print("🚫 Network creation failed.")
    else:
        print("🚫 Aborting network creation due to connection failure.")
