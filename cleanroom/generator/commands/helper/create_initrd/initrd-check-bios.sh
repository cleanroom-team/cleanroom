#!/usr/bin/sh

MNENCODE="/usr/bin/initrd-mnencode"
HASH="/usr/bin/md5sum"

HAVE_TPM="no"
PCRS=""
for i in 'tpm0' 'tpm1' 'tpm2' 'tpm3' ; do
    P="/sys/class/tpm/${i}/pcrs"
    if test -r "${P}" ; then
        NEXT=`head -n 17 "${P}"`
	PCRS="${PCRS}${P}:\n${NEXT}"
	HAVE_TPM='yes'
    fi
done

if test "x${HAVE_TPM}" != "xyes" ; then
    echo "**** NO TPM CHIP FOUND ****"
    exit 0
fi

if test -z "${PCRS}" ; then
    echo "**** NO PCRS REGISTERS FOUND ****"
    exit 0
fi

HRESULT=`echo "${PCRS}" | "${HASH}" | cut -d' ' -f1`
RESULT=`printf "${HRESULT}" | "${MNENCODE}"`
echo "${HRESULT}"
echo "${RESULT}"

