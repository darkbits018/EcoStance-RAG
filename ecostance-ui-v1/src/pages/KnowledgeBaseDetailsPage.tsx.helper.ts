
// Helper function to map mime types/extensions to Document fileType
const mapFileType = (mimeType: string | undefined): any => {
    const type = (mimeType || '').toLowerCase();
    if (type.includes('pdf')) return 'pdf';
    if (type.includes('word') || type.includes('docx') || type.includes('doc')) return 'docx';
    if (type.includes('text') || type.includes('txt')) return 'txt';
    if (type.includes('csv')) return 'csv';
    if (type.includes('json')) return 'json';
    if (type.includes('wav')) return 'wav';
    if (type.includes('mp3')) return 'mp3';
    if (type.includes('m4a')) return 'm4a';
    if (type.includes('ogg')) return 'ogg';
    if (type.includes('audio')) return 'audio';
    if (type.includes('markdown') || type.includes('md')) return 'md';
    return 'unknown';
};
