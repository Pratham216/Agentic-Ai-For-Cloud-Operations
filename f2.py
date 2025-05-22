import openstack
import traceback

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFgAYEia-oTMeyinY0ZPMF2gnGyGLDvzAwYefysN_yUKp2VnvJref8LnXKwxKdDsDN5kR2Io75omm3Kgdui6zaMUfPK3la022niV4pTS9NDTgQSobQ4jyI6xjIoVNQ7mkTZ_SRjU0UY4A4h6NbmefZvJBRMfBwG_FwMg6RWSlncMQTds',
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

def find_servers_by_name(conn, vm_name):
    try:
        servers = [server for server in conn.compute.servers() if server.name == vm_name]
        return servers
    except Exception as e:
        print(f"❌ Error retrieving servers:\n{e}")
        traceback.print_exc()
        return []

def resize_vm(conn, server_id, new_flavor_id):
    try:
        server = conn.compute.get_server(server_id)
        if not server:
            print(f"❌ VM with ID '{server_id}' not found.")
            return False

        print(f"🔄 Resizing VM '{server.name}' (ID: {server.id}) to flavor '{new_flavor_id}'...")
        conn.compute.resize_server(server, new_flavor_id)

        # Wait for the server to enter VERIFY_RESIZE status
        conn.compute.wait_for_status(
            conn.compute.get_server(server_id),
            status='VERIFY_RESIZE',
            failures=['ERROR'],
            interval=5,
            wait=300
        )

        # Confirm the resize by calling the API directly
        conn.compute.post(
            f'servers/{server_id}/action',
            json={"confirmResize": None}
        )

        print(f"✅ VM '{server.name}' resized successfully to flavor '{new_flavor_id}'.")
        return True
    except Exception as e:
        print(f"❌ Failed to resize VM: {e}")
        traceback.print_exc()
        return False

def main():
    conn = connect_openstack()
    if not conn:
        print("🚫 Aborting VM resize due to connection failure.")
        return

    vm_name = "dev-box"

    # Replace this with the flavor name or ID you want to resize to
    # Example flavor from your list:
    # new_flavor_id = "M.32"  # flavor name
    new_flavor_id = "316f94a3-c2b5-4068-8a71-1c61c901c0f7"  # flavor ID for M.32

    servers = find_servers_by_name(conn, vm_name)

    if not servers:
        print(f"❌ No VM found with the name '{vm_name}'.")
        return

    if len(servers) == 1:
        # Only one server found, proceed to resize
        server_id = servers[0].id
        success = resize_vm(conn, server_id, new_flavor_id)
        if not success:
            print("🚫 VM resize failed.")
    else:
        # Multiple servers found with the same name
        print(f"⚠️ Multiple VMs found with the name '{vm_name}':")
        for idx, server in enumerate(servers, start=1):
            print(f"  {idx}. ID: {server.id}, Status: {server.status}, Name: {server.name}")

        # Ask user to select which VM to resize
        while True:
            try:
                choice = int(input(f"Enter the number (1-{len(servers)}) of the VM you want to resize: "))
                if 1 <= choice <= len(servers):
                    selected_server_id = servers[choice - 1].id
                    break
                else:
                    print("❌ Invalid choice. Please enter a valid number.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        success = resize_vm(conn, selected_server_id, new_flavor_id)
        if not success:
            print("🚫 VM resize failed.")

if __name__ == "__main__":
    main()
