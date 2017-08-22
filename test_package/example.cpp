#include <iostream>
#include "librdkafka/rdkafkacpp.h"

int main() {
    std::cout << "librdkafka version " << RdKafka::version_str() << std::endl;
}
