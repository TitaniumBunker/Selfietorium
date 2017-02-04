#!/usr/bin/python
# coding=utf-8
import cups


class Printer:
    """A class for capturing images from a fake camera"""
    def __init__(self, printer_name):
        """Constructor for this object."""
        print("Starting Fake Printer Object")
        self.conn = cups.Connection()
        printers = self.conn.getPrinters()

        printer = [p for p in printers if p == printer_name]
        if (len(printer) > 0):
            print "Found Printer"
            print printer[0]
            self.printer_name = printer[0]
            #self.conn.printFile(printer[0],photo,'Selfietorium',{})
        else:
            raise ValueError('Unable to find printer : ' + printer_name)

    def print_photo(self, photo, print_job_name):
        """
        Prints a photo file using the specified job name to the printer.
        :param photo: Photo file
        :param print_job_name: Job Name
        """
        self.conn.printFile(self.printer_name, photo, print_job_name, {})


if __name__ == '__main__':

    # Add sample Code here
    print "hello - I am a print example"
    c = Printer('PDF')
    c.print_photo('output.svg', 'test')
