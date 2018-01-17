project = "conan-librdkafka"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

images = [
<<<<<<< HEAD
  'centos7': [
    'name': 'essdmscdm/centos7-build-node:1.0.1',
    'sh': 'sh'
  ],
  'centos7-gcc6': [
    'name': 'essdmscdm/centos7-gcc6-build-node:1.0.0',
    'sh': '/usr/bin/scl enable rh-python35 devtoolset-6 -- /bin/bash'
  ],
  'debian9': [
  'name': 'essdmscdm/debian9-build-node:1.0.0',
  'sh': 'sh'
  ],
  'fedora25': [
    'name': 'essdmscdm/fedora25-build-node:1.0.0',
    'sh': 'sh'
  ],
  'ubuntu1604': [
    'name': 'essdmscdm/ubuntu16.04-build-node:1.0.0',
    'sh': 'sh'
  ],
  'ubuntu1710': [
    'name': 'essdmscdm/ubuntu17.10-build-node:1.0.0',
    'sh': 'sh'
=======
  'centos': [
    'name': 'essdmscdm/centos-build-node:0.9.4',
    'sh': 'sh',
    'shared': true,
    'static': true
  ],
  'centos-gcc6': [
    'name': 'essdmscdm/centos-gcc6-build-node:0.3.4',
    'sh': '/usr/bin/scl enable rh-python35 devtoolset-6 -- /bin/bash',
    'shared': true,
    'static': true
  ],
  'fedora': [
    'name': 'essdmscdm/fedora-build-node:0.4.2',
    'sh': 'sh',
    'shared': true,
    'static': true
  ],
  'debian': [
    'name': 'essdmscdm/debian-build-node:0.1.1',
    'sh': 'sh',
    'shared': true,
    'static': true
  ],
/*
  'ubuntu1604': [
    'name': 'essdmscdm/ubuntu16.04-build-node:0.0.2',
    'sh': 'sh',
    'shared': true,
    'static': tre
  ],
*/
  'ubuntu1710': [
    'name': 'essdmscdm/ubuntu17.10-build-node:0.0.3',
    'sh': 'sh',
    'shared': false,
    'static': true
>>>>>>> c7222392e0e6f6f6595002fa6075f33aedd135e8
  ]
]

base_container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def get_pipeline(image_key) {
  return {
    node('docker') {
      def container_name = "${base_container_name}-${image_key}"
      try {
        def image = docker.image(images[image_key]['name'])
        def custom_sh = images[image_key]['sh']
        def container = image.run("\
          --name ${container_name} \
          --tty \
          --cpus=2 \
          --memory=4GB \
          --network=host \
          --env http_proxy=${env.http_proxy} \
          --env https_proxy=${env.https_proxy} \
          --env local_conan_server=${env.local_conan_server} \
        ")

        stage("${image_key}: Checkout") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            git clone \
              --branch ${env.BRANCH_NAME} \
              https://github.com/ess-dmsc/${project}.git
          \""""
        }  // stage

        stage("${image_key}: Conan setup") {
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            sh """docker exec ${container_name} ${custom_sh} -c \"
              set +x
              conan remote add \
                --insert 0 \
                ${conan_remote} ${local_conan_server} && \
              conan user \
                --password '${CONAN_PASSWORD}' \
                --remote ${conan_remote} \
                ${conan_user} \
                > /dev/null
            \""""
          }  // withCredentials
        }  // stage

        stage("${image_key}: Package") {
          if (images[image_key]['static']) {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create . ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=False \
              --build=outdated
          \""""
          }

          if (images[image_key]['shared']) {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create . ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=True \
              --build=outdated
          \""""
          }
        }  // stage

        stage("${image_key}: Upload") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            upload_conan_package.sh ${project}/conanfile.py \
              ${conan_remote} \
              ${conan_user} \
              ${conan_pkg_channel}
          \""""
        }  // stage
      } finally {
        sh "docker stop ${container_name}"
        sh "docker rm -f ${container_name}"
      }  // finally
    }  // node
  }  // return
}  // def

<<<<<<< HEAD
def get_macos_pipeline() {
=======
def get_osx_pipeline() {
>>>>>>> c7222392e0e6f6f6595002fa6075f33aedd135e8
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
<<<<<<< HEAD
        stage("macOS: Checkout") {
          checkout scm
        }  // stage

        stage("macOS: Conan setup") {
=======
        stage("OSX: Checkout") {
          checkout scm
        }  // stage

        stage("OSX: Conan setup") {
>>>>>>> c7222392e0e6f6f6595002fa6075f33aedd135e8
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            sh "conan user \
<<<<<<< HEAD
              --password '${CONAN_PASSWORD}' \
              --remote ${conan_remote} \
              ${conan_user} \
              > /dev/null"
          }  // withCredentials
        }  // stage

        stage("macOS: Package") {
          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings librdkafka:build_type=Release \
            --options librdkafka:shared=False \
            --build=outdated"

          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings librdkafka:build_type=Release \
            --options librdkafka:shared=True \
            --build=outdated"
        }  // stage

        stage("macOS: Upload") {
          sh "upload_conan_package.sh conanfile.py \
            ${conan_remote} \
            ${conan_user} \
            ${conan_pkg_channel}"
        }  // stage
      }  // dir
=======
                --password '${CONAN_PASSWORD}' \
                --remote ${conan_remote} \
                ${conan_user} \
                > /dev/null"
          }  // withCredentials
        }  // stage

        stage("OSX: Package") {
          sh "conan create ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=False \
              --build=missing && \
            conan create ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=True \
              --build=missing"
        }  // stage

        stage("OSX: Upload") {
          sh "upload_conan_package.sh conanfile.py \
                ${conan_remote} \
                ${conan_user} \
                ${conan_pkg_channel}"
        }
      }
>>>>>>> c7222392e0e6f6f6595002fa6075f33aedd135e8
    }  // node
  }  // return
}  // def

node {
  checkout scm

  def builders = [:]
  for (x in images.keySet()) {
    def image_key = x
    builders[image_key] = get_pipeline(image_key)
  }
<<<<<<< HEAD
  builders['macOS'] = get_macos_pipeline()
=======
  builders['MacOSX'] = get_osx_pipeline()

>>>>>>> c7222392e0e6f6f6595002fa6075f33aedd135e8
  parallel builders

  // Delete workspace when build is done.
  cleanWs()
}
