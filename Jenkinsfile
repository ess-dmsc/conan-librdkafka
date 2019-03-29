@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder

project = "conan-librdkafka"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

containerBuildNodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian9'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804'),
  'alpine': ContainerBuildNode.getDefaultContainerBuildNode('alpine')
]

packageBuilder = new ConanPackageBuilder(this, containerBuildNodes, conan_pkg_channel)
packageBuilder.defineRemoteUploadNode('centos')

builders = packageBuilder.createPackageBuilders { container ->
  packageBuilder.addConfiguration(container, [
    'settings': [
      'librdkafka:build_type': 'Debug'
    ],
    'options': [
      'librdkafka:shared': 'False'
    ]
  ])

  packageBuilder.addConfiguration(container, [
    'options': [
      'librdkafka:shared': 'True'
    ]
  ])

  packageBuilder.addConfiguration(container)
}

node {
  checkout scm

  builders['macOS'] = get_macos_pipeline()
  builders['windows10'] = get_win10_pipeline()
  parallel builders

  // Delete workspace when build is done.
  cleanWs()
}

def get_macos_pipeline() {
  def should_upload
  def conan_upload_flag
  if (conan_pkg_channel == "stable" && env.BRANCH_NAME != "master") {
    should_upload = false
  } else {
    should_upload = true
    if (conan_pkg_channel == "stable") {
      conan_upload_flag = "--no-overwrite"
    } else {
      conan_upload_flag = ""
    }
  }

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

          pkg_name_and_version = sh(
            script: "./get_conan_pkg_name_and_version.sh",
            returnStdout: true
          ).trim()
        }  // stage

        if (should_upload) {
          stage("macOS: Upload") {
            sh "conan upload \
              --all \
              ${conan_upload_flag} \
              --remote ${conan_remote} \
              ${pkg_name_and_version}@${conan_user}/${conan_pkg_channel}"
          }  // stage
        } else {
          echo "Skipping upload"
        }  // else
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
