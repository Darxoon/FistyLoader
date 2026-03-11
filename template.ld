SECTIONS
{
    . = FISTY_BASE_OFFSET;
    .fisty : {
        *(.fisty)
        *(.text)
    }
}
