def project = "conan-librdkafka"
def centos = docker.image('essdmscdm/centos-build-node:0.7.0')
def container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def conan_remote = "ess-dmsc-local"
def conan_user = "ess-dmsc"
def conan_pkg_channel = "testing"

node('docker') {
    def run_args = "\
       --name ${container_name} \
       --tty \
       --network=host \
       --env http_proxy=${env.http_proxy} \
       --env https_proxy=${env.https_proxy} \
       --env local_conan_server=${env.local_conan_server}"

   try {
        container = centos.run(run_args)

        stage('Checkout') {
            sh """docker exec ${container_name} sh -c \"
                git clone https://github.com/ess-dmsc/${project}.git \
                    --branch ${env.BRANCH_NAME}
            \""""
        }

        stage('Conan setup') {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )])
            {
                sh """docker exec ${container_name} sh -c \"
                    set +x
                    export http_proxy=''
                    export https_proxy=''
                    conan remote add \
                        --insert 0 \
                        ${conan_remote} ${local_conan_server}
                    conan user \
                        --password '${CONAN_PASSWORD}' \
                        --remote ${conan_remote} \
                        ${conan_user} \
                        > /dev/null
                \""""
            }
        }

        stage('Package') {
            sh """docker exec ${container_name} sh -c \"
                cd ${project}
                conan create ${conan_user}/${conan_pkg_channel} \
                    --build=missing
            \""""
        }

        stage('Upload') {
            sh """docker exec ${container_name} sh -c \"
                export http_proxy=''
                export https_proxy=''
                cd ${project}
                \# Get package name from conanfile.py.
                pkg_name=$(grep "name = " conanfile.py | awk '{print \$3}')
                \# Remove quotes from package name.
                pkg_name=$(echo \$pkg_name | sed -e "s/\\\"//g")
                conan upload --all --remote ${conan_remote} '\$pkg_name/*'
            \""""
        }
    } finally {
        container.stop()
    }
}
