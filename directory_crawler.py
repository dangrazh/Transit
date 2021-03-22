# from https://stackoverflow.com/questions/27439379/python-ntquerydirectoryfile-file-information-structure

# import sys
import os
import msvcrt
import ctypes
import datetime
import tempfile
from ctypes import wintypes
import pandas as pd
import numpy as np


from profiler import StopWatch

ntdll = ctypes.WinDLL("ntdll")
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def NtError(status):
    err = ntdll.RtlNtStatusToDosError(status)
    return ctypes.WinError(err)


NTSTATUS = wintypes.LONG
STATUS_BUFFER_OVERFLOW = NTSTATUS(0x80000005).value
STATUS_NO_MORE_FILES = NTSTATUS(0x80000006).value
STATUS_INFO_LENGTH_MISMATCH = NTSTATUS(0xC0000004).value

ERROR_DIRECTORY = 0x010B
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 1
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_ATTRIBUTE_DIRECTORY = 0x0010

FILE_INFORMATION_CLASS = wintypes.ULONG
FileDirectoryInformation = 1
FileBasicInformation = 4

LPSECURITY_ATTRIBUTES = wintypes.LPVOID
PIO_APC_ROUTINE = wintypes.LPVOID
ULONG_PTR = wintypes.WPARAM


class UNICODE_STRING(ctypes.Structure):
    _fields_ = (
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.LPWSTR),
    )


PUNICODE_STRING = ctypes.POINTER(UNICODE_STRING)


class IO_STATUS_BLOCK(ctypes.Structure):
    class _STATUS(ctypes.Union):
        _fields_ = (("Status", NTSTATUS), ("Pointer", wintypes.LPVOID))

    _anonymous_ = ("_Status",)
    _fields_ = (("_Status", _STATUS), ("Information", ULONG_PTR))


PIO_STATUS_BLOCK = ctypes.POINTER(IO_STATUS_BLOCK)

ntdll.NtQueryInformationFile.restype = NTSTATUS
ntdll.NtQueryInformationFile.argtypes = (
    wintypes.HANDLE,  # In  FileHandle
    PIO_STATUS_BLOCK,  # Out IoStatusBlock
    wintypes.LPVOID,  # Out FileInformation
    wintypes.ULONG,  # In  Length
    FILE_INFORMATION_CLASS,
)  # In  FileInformationClass

ntdll.NtQueryDirectoryFile.restype = NTSTATUS
ntdll.NtQueryDirectoryFile.argtypes = (
    wintypes.HANDLE,  # In     FileHandle
    wintypes.HANDLE,  # In_opt Event
    PIO_APC_ROUTINE,  # In_opt ApcRoutine
    wintypes.LPVOID,  # In_opt ApcContext
    PIO_STATUS_BLOCK,  # Out    IoStatusBlock
    wintypes.LPVOID,  # Out    FileInformation
    wintypes.ULONG,  # In     Length
    FILE_INFORMATION_CLASS,  # In     FileInformationClass
    wintypes.BOOLEAN,  # In     ReturnSingleEntry
    PUNICODE_STRING,  # In_opt FileName
    wintypes.BOOLEAN,
)  # In     RestartScan

kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = (
    wintypes.LPCWSTR,  # In     lpFileName
    wintypes.DWORD,  # In     dwDesiredAccess
    wintypes.DWORD,  # In     dwShareMode
    LPSECURITY_ATTRIBUTES,  # In_opt lpSecurityAttributes
    wintypes.DWORD,  # In     dwCreationDisposition
    wintypes.DWORD,  # In     dwFlagsAndAttributes
    wintypes.HANDLE,
)  # In_opt hTemplateFile


class FILE_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("CreationTime", wintypes.LARGE_INTEGER),
        ("LastAccessTime", wintypes.LARGE_INTEGER),
        ("LastWriteTime", wintypes.LARGE_INTEGER),
        ("ChangeTime", wintypes.LARGE_INTEGER),
        ("FileAttributes", wintypes.ULONG),
    )


class FILE_DIRECTORY_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("_Next", wintypes.ULONG),
        ("FileIndex", wintypes.ULONG),
        ("CreationTime", wintypes.LARGE_INTEGER),
        ("LastAccessTime", wintypes.LARGE_INTEGER),
        ("LastWriteTime", wintypes.LARGE_INTEGER),
        ("ChangeTime", wintypes.LARGE_INTEGER),
        ("EndOfFile", wintypes.LARGE_INTEGER),
        ("AllocationSize", wintypes.LARGE_INTEGER),
        ("FileAttributes", wintypes.ULONG),
        ("FileNameLength", wintypes.ULONG),
        ("_FileName", wintypes.WCHAR * 1),
    )

    @property
    def FileName(self):
        addr = ctypes.addressof(self) + type(self)._FileName.offset
        size = self.FileNameLength // ctypes.sizeof(wintypes.WCHAR)
        return (wintypes.WCHAR * size).from_address(addr).value


class DirEntry(FILE_DIRECTORY_INFORMATION):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.FileName)

    @classmethod
    def listbuf(cls, buf):
        result = []
        base_size = ctypes.sizeof(cls) - ctypes.sizeof(wintypes.WCHAR)
        offset = 0
        while True:
            fdi = cls.from_buffer(buf, offset)
            if fdi.FileNameLength and fdi.FileName not in (".", ".."):
                cfdi = cls()
                size = base_size + fdi.FileNameLength
                ctypes.resize(cfdi, size)
                ctypes.memmove(ctypes.byref(cfdi), ctypes.byref(fdi), size)
                result.append(cfdi)
            if fdi._Next:
                offset += fdi._Next
            else:
                break
        return result


def isdir(path):
    if not isinstance(path, int):
        return os.path.isdir(path)
    try:
        hFile = msvcrt.get_osfhandle(path)
    except IOError:
        return False
    iosb = IO_STATUS_BLOCK()
    info = FILE_BASIC_INFORMATION()
    status = ntdll.NtQueryInformationFile(
        hFile,
        ctypes.byref(iosb),
        ctypes.byref(info),
        ctypes.sizeof(info),
        FileBasicInformation,
    )
    return bool(status >= 0 and info.FileAttributes & FILE_ATTRIBUTE_DIRECTORY)


def ntlistdir(path=None):
    result = []

    if path is None:
        path = os.getcwd()

    if isinstance(path, int):
        close = False
        fd = path
        hFile = msvcrt.get_osfhandle(fd)
    else:
        close = True
        hFile = kernel32.CreateFileW(
            path,
            GENERIC_READ,
            FILE_SHARE_READ,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            None,
        )
        if hFile == INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())
        fd = msvcrt.open_osfhandle(hFile, os.O_RDONLY)

    try:
        if not isdir(fd):
            raise ctypes.WinError(ERROR_DIRECTORY)
        iosb = IO_STATUS_BLOCK()
        info = (ctypes.c_char * 4096)()
        while True:
            status = ntdll.NtQueryDirectoryFile(
                hFile,
                None,
                None,
                None,
                ctypes.byref(iosb),
                ctypes.byref(info),
                ctypes.sizeof(info),
                FileDirectoryInformation,
                False,
                None,
                False,
            )
            if (
                status == STATUS_BUFFER_OVERFLOW
                or iosb.Information == 0
                and status >= 0
            ):
                info = (ctypes.c_char * (ctypes.sizeof(info) * 2))()
            elif status == STATUS_NO_MORE_FILES:
                break
            elif status >= 0:
                sublist = DirEntry.listbuf(info)
                result.extend(sublist)
            else:
                raise NtError(status)
    finally:
        if close:
            os.close(fd)

    return result


def walk_directory(dir_path):
    # print(f"scanning folder: {dir_path}")
    try:
        for entry in ntlistdir(dir_path):  # sys.exec_prefix
            if entry.FileAttributes & FILE_ATTRIBUTE_DIRECTORY:
                # print("recursive call...")
                yield from walk_directory(f"{dir_path}\\{entry.FileName}")
            else:
                # yield f"Path: {dir_path} | File: {entry.FileName}"
                # if entry.FileName == "DISTRIBUTIONS.txt":
                #     print("we found the file...")
                yield (
                    dir_path,
                    entry.FileName,
                    entry.CreationTime,
                    entry.LastWriteTime,
                    entry.ChangeTime,
                    entry.LastAccessTime,
                    entry.AllocationSize,
                )
    except PermissionError as e:
        yield (dir_path, e, 0, 0)


def get_files_in_directories(root_dir):

    watch = StopWatch("Win32 API")
    dir_list = []

    watch.start_run()
    for elem in walk_directory(root_dir):
        # print(elem)
        dir_list.append(elem)
    print(watch.time_run())

    return dir_list


def ad_timestamp(timestamp):

    # coming from: https://stackoverflow.com/questions/51547064/convert-18-digit-ldap-filetime-timestamps-to-human-readable-date/54131481
    if timestamp != 0:
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(
            seconds=timestamp / 10000000
        )
    # return datetime.datetime.fromtimestamp((entry.CreationTime / 10000000) - 11644473600)
    return np.nan


def summary_rpt(df, df_grouped, df_old_folders):

    total_space = df_old_folders["SizeOnDisk"].sum() / 1_048_576
    no_of_files = df_old_folders["File"].sum()

    out = (
        "\n----------------------------------------------------\n"
        f"No of files analyzed: {len(df.index):,}\n"
        f"No of folders analyzed:  {len(df_grouped.index):,}\n"
        f"No of folder with old files only: {len(df_old_folders.index):,}\n"
        f"No of old files: {no_of_files:,}\n"
        f"Total space occupied by old files: {total_space:,.2f} MB\n"
        "----------------------------------------------------\n"
    )

    return out


def export_to_excel(df_to_export):

    temp_path = tempfile.gettempdir()
    file_out_name = ""

    with pd.ExcelWriter(
        file_out_name, engine="xlsxwriter"
    ) as writer:  # pylint: disable=abstract-class-instantiated
        df_to_export.to_excel(writer, index=False, sheet_name="DirectoryCrawler")

    return file_out_name


if __name__ == "__main__":

    root_dir = "Q:\\"
    date_limit = datetime.datetime(2015, 1, 1, 0, 00, 00, 0000)
    date_to_check = "ChangeTime"

    # Get the file list from directory
    files = get_files_in_directories(root_dir)

    # Pandas DF creation
    watch = StopWatch("Pandas DF creation")
    watch.start_run()
    df = pd.DataFrame(
        files,
        columns=[
            "Path",
            "File",
            "CreationTime",
            "LastWriteTime",
            "ChangeTime",
            "LastAccessTime",
            "SizeOnDisk",
        ],
    )
    print(watch.time_run())

    # Pandas create date columns
    watch = StopWatch("Pandas create date columns")
    watch.start_run()
    df["CreationTime"] = df["CreationTime"].fillna(0).apply(ad_timestamp)
    df["LastWriteTime"] = df["LastWriteTime"].fillna(0).apply(ad_timestamp)
    df["ChangeTime"] = df["ChangeTime"].fillna(0).apply(ad_timestamp)
    df["LastAccessTime"] = df["LastAccessTime"].fillna(0).apply(ad_timestamp)
    print(watch.time_run())

    # Pandas group by
    watch = StopWatch("Pandas DF group by")
    watch.start_run()
    df_grouped = df.groupby("Path").agg(
        {"File": "count", "SizeOnDisk": "sum", date_to_check: "max"}
    )
    print(watch.time_run())

    # Pandas filter
    df_old_folders = df_grouped[df_grouped[date_to_check] < date_limit]

    # Print the summary report
    print(summary_rpt(df, df_grouped, df_old_folders))

    # create an excel with "old folders"
    excel = export_to_excel(df_old_folders)
    watch.print_with_time(f"Excel with old folders created: {excel}")
    watch.print_with_time("Done...")