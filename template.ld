SECTIONS
{
    . = 0x24FC000;
    .fisty : {
        *(.fisty)
        *(.text)
    }
}
