import React, { useEffect, useState } from 'react';
import { emailService, type Email } from '../services/emailService';
import { Search, ChevronLeft, ChevronRight, MailOpen, Calendar } from 'lucide-react';

export const EmailBrowserPage: React.FC = () => {
    const [emails, setEmails] = useState<Email[]>([]);
    const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingContent, setLoadingContent] = useState(false);
    const [search, setSearch] = useState('');

    // Pagination (basic)
    const [page, setPage] = useState(1);
    const limit = 20;

    useEffect(() => {
        fetchEmails();
    }, [page, search]); // Re-fetch when page or search changes

    // Debouncing search is better, but keeping it simple for now
    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(1);
        fetchEmails();
    }

    const fetchEmails = async () => {
        setLoading(true);
        try {
            const data = await emailService.getEmails({ page, limit, search });
            setEmails(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectEmail = async (email: Email) => {
        setSelectedEmail(email); // Show available data immediately

        // If body is missing (listing optimization), fetch full details
        if (!email.body_html && !email.body_text) {
            setLoadingContent(true);
            try {
                const fullEmail = await emailService.getEmail(email.id);
                setSelectedEmail(fullEmail);
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingContent(false);
            }
        }
    };


    // Helper to generate color from string
    const getAvatarColor = (name: string) => {
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        const h = Math.abs(hash) % 360;
        return `hsl(${h}, 70%, 50%)`;
    };

    const getInitials = (name: string) => {
        return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    };

    return (
        <div className="container-main" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 2rem)', gap: '1rem' }}>
            {/* Header Toolbar */}
            <div className="glass-panel" style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                        <MailOpen size={24} />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Inbox</h1>
                        <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{emails.length} messages loaded</p>
                    </div>
                </div>

                <form onSubmit={handleSearch} style={{ position: 'relative', width: '400px' }}>
                    <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                    <input
                        className="glass-input"
                        style={{ paddingLeft: '2.5rem', width: '100%', borderRadius: '1rem', background: 'rgba(0,0,0,0.2)' }}
                        placeholder="Search by sender, subject, or content..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </form>
            </div>

            {/* Main Split View */}
            <div style={{ flex: 1, display: 'flex', gap: '1rem', overflow: 'hidden' }}>

                {/* Left: Email List */}
                <div className="glass-panel" style={{ flex: '0 0 450px', display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden', borderRight: '1px solid var(--border-glass)' }}>
                    <div style={{ flex: 1, overflowY: 'auto' }} className="custom-scrollbar">
                        {loading ? (
                            <div className="flex-center" style={{ height: '200px', flexDirection: 'column', gap: '1rem' }}>
                                <div className="loader"></div>
                                <span style={{ color: 'var(--color-text-muted)' }}>Syncing emails...</span>
                            </div>
                        ) : emails.length === 0 ? (
                            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                                <p>No emails found.</p>
                            </div>
                        ) : (
                            emails.map(email => {
                                const isSelected = selectedEmail?.id === email.id;
                                const senderName = email.sender.split('<')[0].trim().replace('"', '');
                                return (
                                    <div
                                        key={email.id}
                                        onClick={() => handleSelectEmail(email)}
                                        style={{
                                            padding: '1.25rem',
                                            borderBottom: 'var(--border-glass)',
                                            cursor: 'pointer',
                                            background: isSelected ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                                            borderLeft: isSelected ? '3px solid var(--color-primary)' : '3px solid transparent',
                                            transition: 'all 0.2s ease'
                                        }}
                                        className="hover:bg-white/5"
                                    >
                                        <div style={{ display: 'flex', gap: '1rem' }}>
                                            {/* Avatar */}
                                            <div style={{
                                                width: '40px', height: '40px', borderRadius: '50%',
                                                background: `linear-gradient(135deg, ${getAvatarColor(senderName)}aa, ${getAvatarColor(senderName)})`,
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                fontSize: '0.9rem', fontWeight: 'bold', color: 'white',
                                                flexShrink: 0, textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                                            }}>
                                                {getInitials(senderName)}
                                            </div>

                                            {/* Info */}
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', alignItems: 'baseline' }}>
                                                    <span style={{ fontWeight: '600', fontSize: '0.95rem', color: isSelected ? 'white' : 'var(--color-text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '160px' }}>
                                                        {senderName}
                                                    </span>
                                                    <span style={{ fontSize: '0.75rem', color: isSelected ? 'var(--color-text-vibrant)' : 'var(--color-text-muted)' }}>
                                                        {new Date(email.received_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                                    </span>
                                                </div>
                                                <div style={{ fontWeight: isSelected ? '600' : '500', fontSize: '0.9rem', marginBottom: '0.35rem', color: isSelected ? 'white' : 'var(--color-text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                    {email.subject || '(No Subject)'}
                                                </div>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: '1.4' }}>
                                                    {email.snippet}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>

                    {/* Pagination */}
                    <div style={{ padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderTop: 'var(--border-glass)', display: 'flex', justifyContent: 'center', gap: '1rem', alignItems: 'center' }}>
                        <button
                            className="glass-button secondary icon-only"
                            disabled={page === 1}
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Page {page}</span>
                        <button
                            className="glass-button secondary icon-only"
                            onClick={() => setPage(p => p + 1)}
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>

                {/* Right: Detail View */}
                <div className="glass-panel" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', padding: 0, position: 'relative' }}>
                    {selectedEmail ? (
                        <>
                            {/* Email Header */}
                            <div style={{ padding: '2rem', borderBottom: 'var(--border-glass)', background: 'rgba(0,0,0,0.1)' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', lineHeight: 1.3 }}>{selectedEmail.subject || '(No Subject)'}</h2>
                                <div style={{ display: 'flex', alignItems: 'flex-start', justifyItems: 'center', gap: '1rem' }}>

                                    <div style={{
                                        width: '48px', height: '48px', borderRadius: '50%',
                                        background: `linear-gradient(135deg, ${getAvatarColor(selectedEmail.sender)}aa, ${getAvatarColor(selectedEmail.sender)})`,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '1.2rem', fontWeight: 'bold', color: 'white',
                                        flexShrink: 0, boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                                    }}>
                                        {getInitials(selectedEmail.sender.split('<')[0].replace('"', ''))}
                                    </div>

                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                                            <div>
                                                <div style={{ fontWeight: '600', fontSize: '1.1rem' }}>{selectedEmail.sender}</div>
                                                <div style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
                                                    To: {selectedEmail.recipients}
                                                </div>
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--color-text-muted)', background: 'rgba(255,255,255,0.05)', padding: '0.3rem 0.8rem', borderRadius: '1rem' }}>
                                                <Calendar size={14} />
                                                <span>{new Date(selectedEmail.received_at).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Email Body Container */}
                            <div style={{ flex: 1, overflowY: 'auto', padding: '2rem' }} className="custom-scrollbar">
                                {loadingContent ? (
                                    <div className="flex-center" style={{ height: '200px', flexDirection: 'column', gap: '1rem', color: 'var(--color-text-muted)' }}>
                                        <div className="loader"></div>
                                        <span>Loading content...</span>
                                    </div>
                                ) : (
                                    <div className="email-content-wrapper" style={{
                                        color: 'var(--color-text-main)',
                                        lineHeight: 1.6,
                                        fontFamily: "'Segoe UI', Roboto, sans-serif",
                                        background: 'rgba(0,0,0,0.2)', // Darker glass
                                        padding: '40px',
                                        borderRadius: '16px',
                                        border: '1px solid var(--border-glass)'
                                    }}>
                                        <div
                                            dangerouslySetInnerHTML={{ __html: selectedEmail.body_html || selectedEmail.body_text?.replace(/\n/g, '<br/>') || '<i style="color:gray">No content</i>' }}
                                            style={{ color: 'inherit' }}
                                        />
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--color-text-muted)', opacity: 0.5 }}>
                            <div style={{
                                width: '120px', height: '120px', borderRadius: '50%',
                                background: 'rgba(255,255,255,0.03)', display: 'flex',
                                alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem',
                                border: '1px solid rgba(255,255,255,0.05)'
                            }}>
                                <MailOpen size={64} style={{ opacity: 0.5 }} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>No Email Selected</h3>
                            <p>Choose an email from the list to view its contents.</p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

