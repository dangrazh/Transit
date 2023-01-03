import random
import string
import sys

from timeit import default_timer as timer


class XmlParser:
    def __init__(self, file_path, file_name, opts="r"):

        # ensure we have a path with trailing /
        if file_path[-1:] != "/" and file_path[-1:] != "\\":
            file_path = file_path + "/"

        self.file_path = file_path
        self.file_name = file_name
        self.file_name_out = file_path + file_name.replace(".", "_") + "_output.csv"
        self.opts = opts
        print(f"Output will be written to: {self.file_name_out}")

        self.doc_string = self._read_file_to_string()
        self.tot_no_of_recs = self.doc_string.count("<Ntry>")
        self.no_of_rec = 0
        self.soup = None
        self.top_node = None

        # the actual content tags to be processed
        self.pg_number = None
        self.svcr_ref = None
        self.ustrd = None

    def _read_file_to_string(self):
        """Return the sample XML file as a string."""

        # file_path, file_name, opts

        file_path_name = self.file_path + self.file_name
        with open(file_path_name, self.opts) as xml:
            return xml.read()

    def _write_record(self, record, type="data"):
        if type == "data":
            mode = "a"
        elif type == "header":
            mode = "w"
        else:
            mode = "a"

        with open(self.file_name_out, mode) as f:
            rec_out = ""
            for itm in record:
                rec_out = rec_out + itm + ";"
            f.write(f"{rec_out}\n")

    def parse_bs4(self):
        from bs4 import BeautifulSoup as bs

        # timer_start = timer()

        self.soup = bs(self.doc_string, "xml")
        self.top_node = self.soup("BkToCstmrStmt")[0]

        self._bs4_traverse_document_tree(self.top_node)
        print("")

    def _bs4_traverse_document_tree(self, bs_elem):

        if str(type(bs_elem)) == "<class 'bs4.element.Tag'>":
            if bs_elem.name:
                if bs_elem.string and len(list(bs_elem.descendants)) == 1:
                    # Tag with value and no further descendants -> we are at the bottom of the tree, print both the tag and the value
                    if bs_elem.name == "AcctSvcrRef":
                        # print("AcctSvcrRef found", end="|")
                        self.svcr_ref = bs_elem.string
                    elif bs_elem.name == "PgNb":
                        self.pg_number = bs_elem.string
                    elif bs_elem.name == "Ustrd":
                        self.ustrd = bs_elem.string
                    else:
                        pass

                else:
                    # element is a node
                    if bs_elem.name == "Ntry":
                        self.no_of_rec += 1
                        print(
                            f"Processing element {self.no_of_rec} of {self.tot_no_of_recs}...",
                            end="\r",
                        )
                        if self.svcr_ref and self.pg_number:
                            record = (self.pg_number, self.svcr_ref, self.ustrd)
                            self._write_record(record, "data")
                        else:
                            # write the header
                            record = ("PgNb", "AcctSvcrRef", "Ustrd")
                            self._write_record(record, "header")

                for child in bs_elem.children:
                    self._bs4_traverse_document_tree(child)


# -------------------------------------------------------------------------------
# The script entry point
# -------------------------------------------------------------------------------
if __name__ == "__main__":

    # # command line arguments ------------------------------------------------------
    if len(sys.argv) == 3:
        filepath = sys.argv[1]
        filename = sys.argv[2]
    else:
        print("Invalid arguments supplied, please supply a filepath + a filename")
        sys.exit(1)

    # xml_as_string = sample_xml("r")
    # xml_as_bytes = sample_xml("rb")

    # print(type(xml_as_string))
    # print(type(xml_as_bytes))

    timer_start = timer()

    parser = XmlParser(filepath, filename, "r")

    parser.parse_bs4()
    print(f"No of records processed: {parser.no_of_rec}")

    seconds = timer() - timer_start
    print(f"Processed file in {seconds} seconds")
