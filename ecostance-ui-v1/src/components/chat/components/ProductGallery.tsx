import React from 'react';
import { Card } from '../../ui/Card';
import { Icons } from '../../icons';
import { Button } from '../../ui/Button';

interface Product {
    name: string;
    image?: string;
    price: string | number;
    eco_rating?: number | string;
    description?: string;
}

interface ProductGalleryProps {
    products: Product[];
}

export const ProductGallery: React.FC<ProductGalleryProps> = ({ products }) => {
    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 mb-2">
                <Icons.LayoutGrid className="w-4 h-4 text-primary" />
                <span className="text-sm font-semibold text-text">Recommended Products</span>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
                {products.map((product, idx) => (
                    <Card key={idx} className="min-w-[200px] max-w-[200px] flex-shrink-0 p-0 overflow-hidden border-border bg-background hover:border-primary transition-colors">
                        {product.image ? (
                            <img src={product.image} alt={product.name} className="w-full h-32 object-cover" />
                        ) : (
                            <div className="w-full h-32 bg-surface flex items-center justify-center text-text-secondary">
                                <Icons.FileText className="w-8 h-8 opacity-20" />
                            </div>
                        )}
                        <div className="p-3">
                            <h5 className="text-sm font-medium text-text truncate" title={product.name}>
                                {product.name}
                            </h5>
                            <div className="flex items-center justify-between mt-1">
                                <span className="text-sm font-bold text-primary">${product.price}</span>
                                {product.eco_rating && (
                                    <div className="flex items-center gap-1 bg-green-500/10 text-green-500 px-1.5 py-0.5 rounded text-[10px] font-bold">
                                        <Icons.Sparkles className="w-2.5 h-2.5" />
                                        {product.eco_rating}
                                    </div>
                                )}
                            </div>
                            <Button size="sm" className="w-full mt-3 h-8 text-xs" variant="outline">
                                View Details
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};
