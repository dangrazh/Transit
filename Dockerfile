# Filename: Dockerfile
# Cross-compile Rust programs to Windows (x86_64) from a UBI8 container
FROM registry.access.redhat.com/ubi8/ubi:latest

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:${PATH}

# Enable the CodeReady Builder repo (dependency for EPEL) and EPEL 
RUN dnf -y install 'dnf-command(config-manager)' && \
    dnf config-manager --add-repo \
        "https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi8/8/$(arch)/codeready-builder/os/" && \
    dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

# Install some basics
RUN dnf -y update && \
    dnf -y install --nogpgcheck \
        ca-certificates \
        curl \
        gcc \
        gcc-c++ \
        git \
        make && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Install Rust via rustup and add the Windows msvc target
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
        sh -s -- -y --profile minimal --default-toolchain stable && \
    rustup toolchain install nightly --profile minimal && \
    rustup target add x86_64-pc-windows-msvc

#Install cargo-xwin 
RUN cargo install cargo-xwin

# Tell Cargo / cc-rs which cross-compiler to use for the Windows target
# ENV CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER=x86_64-w64-mingw32-gcc \
#     CC_x86_64_pc_windows_gnu=x86_64-w64-mingw32-gcc \
#     CXX_x86_64_pc_windows_gnu=x86_64-w64-mingw32-g++

# Set the working directory in the container
WORKDIR /work

# Copy project files into the container
COPY xml2xls_claude/Cargo.toml \
     xml2xls_claude/rust-toolchain.toml \
     xml2xls_claude/tabledef.yaml \
     xml2xls_claude/build.rs \
     xml2xls_claude/app_icon.ico \
     ./
COPY xml2xls_claude/src/ ./src/

CMD ["bash"]
