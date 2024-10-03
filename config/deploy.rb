# config valid for current version and patch releases of Capistrano
require 'json'

lock "~> 3.19.1"

set :application, "my_app_name"
set :repo_url, "git@example.com:me/my_repo.git"

set :deploy_to, "/tmp/cardcraft"

vars = JSON.parse(File.read(Dir.pwd.concat("/config/deploy/prod.json")))

# @todo for a fresh server
# - setup docker
# - setup python runtime and its prerequisites


task "typechecks" do
  run_locally do
    execute (
      ["cd", "projects/cardcraft-web", "&&"] +
      [
        "poetry",
        "run",
        "mypy",
        "--disable-error-code=import-untyped",
        "--disable-error-code=import-not-found",
        "--show-error-context",
        "--pretty",
        "--soft-error-limit=1",
        "--check-untyped-defs",
        "../../bases/cardcraft/app"
      ]
    ).join " "
  end
end

task "tests" do
  run_locally do
    execute (
      ["cd", "projects/cardcraft-web", "&&"] +
      [
        "poetry",
        "run",
        "python3",
        "-m",
        "unittest",
        "discover",
        "-s",
        "cardcraft/app"
      ]
    ).join " "
  end
end

task "up" do
  invoke "typechecks"
  invoke "tests"

  on roles ["web"] do |host|
    execute "rm -rf #{deploy_to}"
  end

  run_locally do
    execute "rsync -r -l #{Dir.pwd}/ #{vars['user']}@#{vars['host']}:#{deploy_to}/"
  end

  on roles ["web"] do |host|
    execute "cd #{deploy_to} && git checkout . && git status"
  end
end

task "web-start" do
  on roles ["web"] do |host|
    execute "cd #{deploy_to}/projects/cardcraft-web && ./start.sh"
  end
end

task "web-stop" do
  on roles ["web"] do |host|
    execute "cd #{deploy_to}/projects/cardcraft-web && ./stop.sh"
  end
end

# Default branch is :master
# ask :branch, `git rev-parse --abbrev-ref HEAD`.chomp

# Default deploy_to directory is /var/www/my_app_name
# set :deploy_to, "/var/www/my_app_name"

# Default value for :format is :airbrussh.
# set :format, :airbrussh

# You can configure the Airbrussh format using :format_options.
# These are the defaults.
# set :format_options, command_output: true, log_file: "log/capistrano.log", color: :auto, truncate: :auto

# Default value for :pty is false
# set :pty, true

# Default value for :linked_files is []
# append :linked_files, "config/database.yml", 'config/master.key'

# Default value for linked_dirs is []
# append :linked_dirs, "log", "tmp/pids", "tmp/cache", "tmp/sockets", "public/system", "vendor", "storage"

# Default value for default_env is {}
# set :default_env, { path: "/opt/ruby/bin:$PATH" }

# Default value for local_user is ENV['USER']
# set :local_user, -> { `git config user.name`.chomp }

# Default value for keep_releases is 5
# set :keep_releases, 5

# Uncomment the following to require manually verifying the host key before first deploy.
# set :ssh_options, verify_host_key: :secure
