project = "conan-librdkafka"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "testing"

images = [
  'centos7': [
    'name': 'essdmscdm/centos7-build-node:2.1.0',
    'sh': 'sh'
  ]//,
  // 'centos7-gcc6': [
  //   'name': 'essdmscdm/centos7-gcc6-build-node:3.0.0 ',
  //   'sh': '/usr/bin/scl enable rh-python35 devtoolset-6 -- /bin/bash'
  // ],
  // 'debian9': [
  // 'name': 'essdmscdm/debian9-build-node:2.0.0',
  // 'sh': 'sh'
  // ],
  // 'fedora25': [
  //   'name': 'essdmscdm/fedora25-build-node:2.0.0',
  //   'sh': 'sh'
  // ],
  // 'ubuntu1804': [
  //   'name': 'essdmscdm/ubuntu18.04-build-node:1.0.0',
  //   'sh': 'sh'
  // ]
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

        stage("${image_key}: Conan local server setup") {
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

        stage("${image_key}: Conan remote ess-dmsc setup") {
          withCredentials([
            usernamePassword(
              credentialsId: 'cow-bot-bintray-username-and-api-key',
              passwordVariable: 'COWBOT_PASSWORD',
              usernameVariable: 'COWBOT_USERNAME'
            )
          ]) {
            sh """docker exec ${container_name} ${custom_sh} -c \"
              set +x
              conan user \
                --password '${COWBOT_PASSWORD}' \
                --remote ess-dmsc \
                ${COWBOT_USERNAME} \
                > /dev/null
            \""""
          }  // withCredentials
        }  // stage

        stage("${image_key}: Package") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create . ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=False \
              --build=outdated
          \""""

          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create . ${conan_user}/${conan_pkg_channel} \
              --settings librdkafka:build_type=Release \
              --options librdkafka:shared=True \
              --build=outdated
          \""""

          // Get package name and version
          pkg_name_and_version = sh(
            script: """docker exec ${container_name} ${custom_sh} -c \"
                cd ${project} &&
                conan info . | awk -F'@' 'NR==1{print \\\$1}'
              \"""",
            returnStdout: true
          ).trim()
        }  // stage

        echo "${pkg_name_and_version}"

        // stage("${image_key}: Local upload") {
        //   sh """docker exec ${container_name} ${custom_sh} -c \"
        //     conan upload \
        //       --no-overwrite \
        //       --remote ${conan_remote} \
        //       ${pkg_name_and_version}@${conan_user}/${conan_pkg_channel}
        //   \""""
        //
        // stage("${image_key}: Remote upload") {
        //   sh """docker exec ${container_name} ${custom_sh} -c \"
        //     conan upload \
        //       --all \
        //       --no-overwrite \
        //       --remote ess-dmsc \
        //       ${pkg_name_and_version}@${conan_user}/${conan_pkg_channel}
        //   \""""
        // }  // stage
      } finally {
        sh "docker stop ${container_name}"
        sh "docker rm -f ${container_name}"
      }  // finally
    }  // node
  }  // return
}  // def

def get_macos_pipeline() {
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
        stage("macOS: Checkout") {
          checkout scm
        }  // stage

        stage("macOS: Conan setup") {
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            sh "conan user \
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
    }  // node
  }  // return
}  // def

def get_win10_pipeline() {
  return {
    node('windows10') {
      // Use custom location to avoid Win32 path length issues
      ws('c:\\jenkins\\') {
      cleanWs()
      dir("${project}") {
        stage("win10: Checkout") {
          checkout scm
        }  // stage

        stage("win10: Conan setup") {
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            bat """C:\\Users\\dmgroup\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\conan.exe user \
              --password ${CONAN_PASSWORD} \
              --remote ${conan_remote} \
              ${conan_user}"""
          }  // withCredentials
        }  // stage

        stage("win10: Package") {
          //bat """C:\\Users\\dmgroup\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\conan.exe \
          //  create . ${conan_user}/${conan_pkg_channel} \
          //  --settings librdkafka:build_type=Release \
          //  --options librdkafka:shared=False \
          //  --build=outdated"""

          bat """C:\\Users\\dmgroup\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\conan.exe \
            create . ${conan_user}/${conan_pkg_channel} \
            --settings librdkafka:build_type=Release \
            --options librdkafka:shared=True \
            --build=outdated"""
        }  // stage

        stage("win10: Upload") {
          //sh "upload_conan_package.sh conanfile.py \
          //  ${conan_remote} \
           // ${conan_user} \
           // ${conan_pkg_channel}"
        }  // stage
      }  // dir
      }
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
  builders['macOS'] = get_macos_pipeline()
  builders['windows10'] = get_win10_pipeline()
  parallel builders

  // Delete workspace when build is done.
  cleanWs()
}
