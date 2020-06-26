FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y software-properties-common \
                                 wget \
                                 zip \
                                 cmake \
                                 git \
                                 zlib1g-dev \
                                 graphviz \
                                 libgraphviz-dev &&\
    add-apt-repository -y ppa:deadsnakes/ppa && apt install -y python3.6 python3-pip && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install ANTS as described here 
# https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS#superbuild-quick-reference
ENV workingDir=/opt/ANTs

RUN git clone https://github.com/ANTsX/ANTs.git && \
    mkdir build install && \
    cd build && \
    cmake \
        -DCMAKE_INSTALL_PREFIX=${workingDir}/install \
        ../ANTs 2>&1 | tee cmake.log && \
    make -j 4 2>&1 | tee build.log && \
    cd ANTS-build && \
    make install 2>&1 | tee install.log



ENV ANTSPATH=/opt/ANTs/install/bin/
ENV PATH=${ANTSPATH}:${PATH}

RUN pip3 install nipype[all] && rm -rf /root/.cache/pip3

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && rm -rf /root/.cache/pip3

RUN mkdir -p /flywheel/v0/templates

 # Chosing these MNI spaces, learn more here:
 # https://www.lead-dbs.org/about-the-mni-spaces/
 
WORKDIR /flywheel/v0/templates

# Download the 2009 asym MNI T1 Templates in zipped nifti format
RUN wget http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_asym_09a_nifti.zip &&\
    unzip mni_icbm152_nlin_asym_09a_nifti.zip && rm mni_icbm152_nlin_asym_09a_nifti.zip

COPY run.py /flywheel/v0/run.py
ENV FLYWHEEL="/flywheel/v0"
WORKDIR $FLYWHEEL
# Run Docker:
# docker run --rm -it --entrypoint=/bin/bash -v /Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/nipype/DockerIO:/tmp flywheel/nipype:0.0.1_1.4.2