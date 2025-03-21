VAGRANTFILE_API_VERSION = "2"
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
ENV['VAGRANT_NO_PARALLEL'] = "0"
ENV['FORWARD_DOCKER_PORTS'] = "1"
ENV['VAGRANT_EXPERIMENTAL'] = "typed_triggers"

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# Define the number of nodes
NODE_COUNT = 10
NODE_IMAGE = "j_dist_node"
NODE_PREFIX = "node-"
NODE_SUBNET = "10.0.1."
NODE_IP_OFFSET = 10
MONITOR_NODE_IP = "10.0.1.2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".*/"
  config.ssh.insert_key = false

  # Build the node image before 'vagrant up'
  config.trigger.before :up, type: :command do |trigger|
    trigger.name = "Build node image"
    trigger.ruby do |env, machine|
      puts "Building docker image:"
      system("docker build . -t \"#{NODE_IMAGE}\"")
    end
  end

  # Define monitor node
  config.vm.define "monitor" do |m|
    m.vm.network "private_network", ip: MONITOR_NODE_IP
    m.vm.hostname = "monitor"

    m.vm.provider "docker" do |d|
      d.build_dir = "."
      d.build_args = ["-t", NODE_IMAGE]
      d.name = "monitor"
      d.create_args = ["--env", "MONITOR_MODE=active"]  # Example argument
      d.has_ssh = true
    end

    m.vm.post_up_message = "Monitor Node up and running."
  end

  # Define base nodes
  (0..NODE_COUNT + 1).each do |i|
    node_name = "#{NODE_PREFIX}#{i - 1}"
    node_ip_addr = "#{NODE_SUBNET}#{NODE_IP_OFFSET + i}"

    config.vm.define node_name do |s|
      s.vm.network "private_network", ip: node_ip_addr
      #s.vm.network "forwarded_port", guest: 80, host: 8080 + i, host_ip: "0.0.0.0"
      s.vm.hostname = node_name

      s.vm.provider "docker" do |d|
        d.build_dir = "."
        d.build_args = ["-t", NODE_IMAGE]
        d.name = node_name
        d.has_ssh = true
      end

      s.vm.post_up_message = "Node #{node_name} up and running."
    end
  end
end

# EOF
