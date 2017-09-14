project = "conan-librdkafka"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "testing"

images = [
    'centos': 'essdmscdm/centos-build-node:0.7.3',
    'centos-gcc6': 'essdmscdm/centos-gcc6-build-node:0.1.0'
]

commands = [
    'centos': 'sh',
    'centos-gcc6': 'scl enable devtoolset-6 rh-python35 /bin/bash'
]

base_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def get_pipeline(image_key) {
    return {
        def container_name = "${base_name}-${image_key}"
        try {
            def image = docker.image(images[image_key])
            def container = image.run("\
                --name ${container_name} \
                --tty \
                --env http_proxy=${env.http_proxy} \
                --env https_proxy=${env.https_proxy} \
            ")

            // Copy sources to container.
            sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"

            stage("Conan setup (${image_key})") {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )]) {
                    sh """docker exec ${container_name} ${commands[image_key]} \"
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

            stage("Package (${image_key})") {
                sh """docker exec ${container_name} ${commands[image_key]} \"
                    cd ${project}
                    conan create ${conan_user}/${conan_pkg_channel} \
                        --build=missing
                \""""
            }

            stage("Upload (${image_key})") {
                sh """docker exec ${container_name} ${commands[image_key]} \"
                    export http_proxy=''
                    export https_proxy=''
                    upload_conan_package.sh ${project}/conanfile.py \
                        ${conan_remote} \
                        ${conan_user} \
                        ${conan_pkg_channel}
                \""""
            }
        } finally {
            sh "docker stop ${container_name}"
            sh "docker rm -f ${container_name}"
        }
    }
}

node('docker') {
    // Delete workspace when build is done
    cleanWs()

    dir("${project}") {
        stage('Checkout') {
            scm_vars = checkout scm
        }
    }

    def builders = [:]
    for (x in images.keySet()) {
        def image_key = x
        builders[image_key] = get_pipeline(image_key)
    }
    parallel builders
}
