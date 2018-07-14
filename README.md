# conan-librdkafka

Conan package for librdkafka

librdkafka is a C and C++ library for Apache Kafka clients
(https://github.com/edenhill/librdkafka).

## Conan Options

* -o librdkafka:with_zlib=False or True
enables the build to compile against Zlib 1.2.11 (provided by the conan community)

* -o librdkafka:with_ssl=False or True
enables the build to compile against OpenSSL 1.1.0g (provided by the conan community)

* -o librdkafka:build_examples=False or True 
builds librdkafka's own example programs

* -o librdkafka:build_tests=False or True
builds librdkafka's own test programs

## Limitations

librdkafka is built without external LZ4 and SASL support.
