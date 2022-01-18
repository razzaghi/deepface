# Set L4T_VERSION, example: 10.2
ARG L4T_VERSION
# Use L4T base docker
FROM nvcr.io/nvidian/nvidia-l4t-base:${L4T_VERSION}

# Install dependencies
RUN apt-get update && \
      DEBIAN_FRONTEND=noninteractive      apt-get install -y --no-install-recommends \
      rsyslog git \
           tzdata \
           libgstrtspserver-1.0-0 \
           libjansson4 \
           libglib2.0 \
           libjson-glib-1.0-0 \
           librabbitmq4 \
           gstreamer1.0-rtsp \
           libcurl4-openssl-dev ca-certificates

#Install libnvvpi1 and vpi1-dev
ADD https://repo.download.nvidia.com/jetson/common/pool/main/libn/libnvvpi1/libnvvpi1_1.0.15_arm64.deb /root
ADD https://repo.download.nvidia.com/jetson/common/pool/main/v/vpi1-dev/vpi1-dev_1.0.15_arm64.deb /root

RUN dpkg -X /root/libnvvpi1_1.0.15_arm64.deb /

RUN dpkg -X /root/vpi1-dev_1.0.15_arm64.deb /

RUN rm /root/libnvvpi1_1.0.15_arm64.deb  \
      /root/vpi1-dev_1.0.15_arm64.deb

RUN ldconfig

# Install DeepStreamSDK using tar package.
ENV DS_REL_PKG deepstream_sdk_v6.0.0_jetson.tbz2

COPY "${DS_REL_PKG}"  \
/

RUN DS_REL_PKG_DIR="${DS_REL_PKG%.tbz2}" && \
cd / && \
tar -xvf "${DS_REL_PKG}" -C / && \
cd /opt/nvidia/deepstream/deepstream && \
./install.sh && \
cd / && \
rm -rf "/${DS_REL_PKG}"

RUN ldconfig

CMD ["/bin/bash"]
WORKDIR /opt/nvidia/deepstream/deepstream

ENV LD_LIBRARY_PATH /usr/local/cuda-10.2/lib64
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all