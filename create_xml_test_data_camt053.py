import random
import secrets
from datetime import datetime

date_time_fmt = "%Y-%m-%d %H:%M:%S"

now = datetime.now()  # current date and time
date_time = now.strftime(date_time_fmt)

print(f"{date_time}: Start... ")

file_name = "p:/Programming/Python/xml_examples/xml_camt053_test_data_large.xml"
with open(file_name, "w") as writer:

    # write the header
    xml_doc_head = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02 camt.053.001.02.xsd">

<BkToCstmrStmt>
  <GrpHdr>
    <MsgId>053D2013-12-27T22:05:03.0N130000005</MsgId>
    <CreDtTm>2013-12-27T22:04:52.0+01:00</CreDtTm>
    <MsgPgntn>
      <PgNb>1</PgNb>
      <LastPgInd>true</LastPgInd>
    </MsgPgntn>
  </GrpHdr>
  <Stmt>
    <Id>0352C5320131227220503</Id>
    <ElctrncSeqNb>130000005</ElctrncSeqNb>
    <CreDtTm>2013-12-27T22:04:52.0+01:00</CreDtTm>
    <Acct>
      <Id>
        <IBAN>DE58740618130100033626</IBAN>
      </Id>
      <Ccy>EUR</Ccy>
      <Ownr>
        <Nm>Testkonto Nummer 2</Nm>
      </Ownr>
      <Svcr>
        <FinInstnId>
          <BIC>GENODEF1PFK</BIC>
          <Nm>VR-Bank Rottal-Inn eG</Nm>
          <Othr>
            <Id>DE 129267947</Id>
            <Issr>UmsStId</Issr>
          </Othr>
        </FinInstnId>
      </Svcr>
    </Acct>
    <Bal>
      <Tp>
        <CdOrPrtry>
          <Cd>PRCD</Cd>
        </CdOrPrtry>
      </Tp>
      <Amt Ccy="EUR">8.50</Amt>
      <CdtDbtInd>CRDT</CdtDbtInd>
      <Dt>
        <Dt>2013-12-27</Dt>
      </Dt>
    </Bal>
    <Bal>
      <Tp>
        <CdOrPrtry>
          <Cd>CLBD</Cd>
        </CdOrPrtry>
      </Tp>
      <Amt Ccy="EUR">18.50</Amt>
      <CdtDbtInd>CRDT</CdtDbtInd>
      <Dt>
        <Dt>2013-12-27</Dt>
      </Dt>
    </Bal>
    """

    writer.write(xml_doc_head)

    # write the trx ntry records
    for idx in range(1, 100_000):  # 0_000

        xml_doc_record = """    <Ntry>
      <Amt Ccy="CHF">[[AMOUNT]]</Amt>
      <CdtDbtInd>CRDT</CdtDbtInd>
      <Sts>BOOK</Sts>
      <BookgDt>
        <Dt>2013-12-27</Dt>
      </BookgDt>
      <ValDt>
        <Dt>2013-12-27</Dt>
      </ValDt>
      <AcctSvcrRef>[[SERVICE_REFERENCE]]</AcctSvcrRef>
      <BkTxCd/>
      <NtryDtls>
        <TxDtls>
          <Refs>
            <EndToEndId>STZV-EtE27122013-11:02-1</EndToEndId>
          </Refs>
          <BkTxCd>
            <Prtry>
              <Cd>NMSC+051</Cd>
              <Issr>ZKA</Issr>
            </Prtry>
          </BkTxCd>
          <RltdPties>
            <Dbtr>
              <Nm>Testkonto Nummer 1</Nm>
            </Dbtr>
            <DbtrAcct>
              <Id>
                <IBAN>DE14740618130000033626</IBAN>
              </Id>
            </DbtrAcct>
            <UltmtDbtr>
              <Nm>keine Information vorhanden</Nm>
            </UltmtDbtr>
            <Cdtr>
              <Nm>Testkonto Nummer 2</Nm>
            </Cdtr>
            <CdtrAcct>
              <Id>
                <IBAN>DE58740618130100033626</IBAN>
              </Id>
            </CdtrAcct>
            <UltmtCdtr>
              <Nm>Testkonto</Nm>
            </UltmtCdtr>
          </RltdPties>
          <RltdAgts>
            <DbtrAgt>
              <FinInstnId>
                <BIC>GENODEF1PFK</BIC>
              </FinInstnId>
            </DbtrAgt>
          </RltdAgts>
          <RmtInf>
            <Ustrd>Dies ist der Freitext fuer diese Buchung</Ustrd>
          </RmtInf>
        </TxDtls>
      </NtryDtls>
    </Ntry>
"""

        amount = f"{idx:,.2f}"
        reference = str(idx).zfill(19)
        xml_doc_record = xml_doc_record.replace("[[AMOUNT]]", amount)
        xml_doc_record = xml_doc_record.replace("[[SERVICE_REFERENCE]]", reference)

        if idx % 10000 == 0:
            now = datetime.now()  # current date and time
            date_time = now.strftime(date_time_fmt)
            print(f"{date_time}: {idx:,} documents written...")

        writer.write(xml_doc_record)

    # write the footer

    xml_doc_foot = """  </Stmt>
</BkToCstmrStmt>
</Document>
"""
    writer.write(xml_doc_foot)

now = datetime.now()  # current date and time
date_time = now.strftime(date_time_fmt)
print(f"{date_time}: Done... ")