import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Skeleton, {
  ShimmerSkeleton,
  OrderCardSkeleton,
  ItemListSkeleton,
  HeaderSkeleton,
  DashboardSkeleton,
  TableSkeleton,
  FormSkeleton,
  TextSkeleton,
  ChartSkeleton
} from '../Skeleton';

describe('Skeleton Component', () => {
  it('should render skeleton with default props', () => {
    const { container } = render(<Skeleton />);
    const skeleton = container.firstChild;
    
    expect(skeleton).toHaveClass('bg-gray-200', 'rounded', 'w-full', 'h-4');
  });

  it('should render with custom width and height', () => {
    const { container } = render(<Skeleton width="w-32" height="h-8" />);
    const skeleton = container.firstChild;
    
    expect(skeleton).toHaveClass('w-32', 'h-8');
  });

  it('should render with custom className', () => {
    const { container } = render(<Skeleton className="custom-class" />);
    const skeleton = container.firstChild;
    
    expect(skeleton).toHaveClass('custom-class');
  });

  it('should render without animation when animated is false', () => {
    const { container } = render(<Skeleton animated={false} />);
    const skeleton = container.firstChild;
    
    expect(skeleton.tagName).toBe('DIV');
  });
});

describe('ShimmerSkeleton Component', () => {
  it('should render shimmer skeleton', () => {
    const { container } = render(<ShimmerSkeleton />);
    const skeleton = container.firstChild;
    
    expect(skeleton).toHaveClass('relative', 'overflow-hidden', 'bg-gray-200', 'rounded');
  });

  it('should have shimmer effect element', () => {
    const { container } = render(<ShimmerSkeleton />);
    const shimmerEffect = container.querySelector('.absolute.inset-0');
    
    expect(shimmerEffect).toBeInTheDocument();
    expect(shimmerEffect).toHaveClass('bg-gradient-to-r');
  });

  it('should render with custom dimensions', () => {
    const { container } = render(<ShimmerSkeleton width="w-64" height="h-16" />);
    const skeleton = container.firstChild;
    
    expect(skeleton).toHaveClass('w-64', 'h-16');
  });
});

describe('OrderCardSkeleton Component', () => {
  it('should render order card skeleton structure', () => {
    const { container } = render(<OrderCardSkeleton />);
    
    // Should have card class
    expect(container.firstChild).toHaveClass('card');
    
    // Should have multiple skeleton elements for different parts of the card
    const skeletons = container.querySelectorAll('.bg-gray-200');
    expect(skeletons.length).toBeGreaterThan(5);
  });

  it('should render status badge skeleton', () => {
    const { container } = render(<OrderCardSkeleton />);
    const statusSkeleton = container.querySelector('.w-16.h-6');
    
    expect(statusSkeleton).toBeInTheDocument();
  });

  it('should render progress bar skeleton', () => {
    const { container } = render(<OrderCardSkeleton />);
    const progressSkeleton = container.querySelector('.w-full.h-2');
    
    expect(progressSkeleton).toBeInTheDocument();
  });

  it('should render avatar skeletons', () => {
    const { container } = render(<OrderCardSkeleton />);
    const avatarSkeletons = container.querySelectorAll('.rounded-full');
    
    expect(avatarSkeletons.length).toBeGreaterThan(0);
  });
});

describe('ItemListSkeleton Component', () => {
  it('should render default number of items', () => {
    const { container } = render(<ItemListSkeleton />);
    const items = container.querySelectorAll('.flex.items-center');
    
    expect(items).toHaveLength(5); // Default items count
  });

  it('should render custom number of items', () => {
    const { container } = render(<ItemListSkeleton items={3} />);
    const items = container.querySelectorAll('.flex.items-center');
    
    expect(items).toHaveLength(3);
  });

  it('should have proper item structure', () => {
    const { container } = render(<ItemListSkeleton items={1} />);
    const item = container.querySelector('.flex.items-center');
    
    expect(item).toHaveClass('p-3', 'bg-white', 'rounded-lg');
  });
});

describe('HeaderSkeleton Component', () => {
  it('should render header skeleton structure', () => {
    const { container } = render(<HeaderSkeleton />);
    const header = container.firstChild;
    
    expect(header).toHaveClass('flex', 'items-center', 'justify-between', 'p-4', 'bg-white');
  });

  it('should render profile section skeletons', () => {
    const { container } = render(<HeaderSkeleton />);
    const avatarSkeleton = container.querySelector('.rounded-full');
    
    expect(avatarSkeleton).toBeInTheDocument();
  });

  it('should render action buttons skeletons', () => {
    const { container } = render(<HeaderSkeleton />);
    const buttonSkeletons = container.querySelectorAll('.rounded-lg');
    
    expect(buttonSkeletons.length).toBeGreaterThan(0);
  });
});

describe('DashboardSkeleton Component', () => {
  it('should render complete dashboard skeleton', () => {
    const { container } = render(<DashboardSkeleton />);
    
    // Should have header skeleton
    expect(container.querySelector('.flex.items-center.justify-between')).toBeInTheDocument();
    
    // Should have stats cards grid
    const statsGrid = container.querySelector('.grid.grid-cols-1.md\\:grid-cols-3');
    expect(statsGrid).toBeInTheDocument();
    
    // Should have order cards grid
    const ordersGrid = container.querySelector('.grid-responsive');
    expect(ordersGrid).toBeInTheDocument();
  });

  it('should render multiple order card skeletons', () => {
    const { container } = render(<DashboardSkeleton />);
    const orderCards = container.querySelectorAll('.card');
    
    expect(orderCards.length).toBeGreaterThan(3); // Stats cards + order cards
  });
});

describe('TableSkeleton Component', () => {
  it('should render table with default rows and columns', () => {
    const { container } = render(<TableSkeleton />);
    
    // Should have header row
    const header = container.querySelector('.px-6.py-3.border-b');
    expect(header).toBeInTheDocument();
    
    // Should have data rows
    const rows = container.querySelectorAll('.px-6.py-4');
    expect(rows).toHaveLength(5); // Default rows
  });

  it('should render custom number of rows and columns', () => {
    const { container } = render(<TableSkeleton rows={3} columns={6} />);
    const rows = container.querySelectorAll('.px-6.py-4');
    
    expect(rows).toHaveLength(3);
  });

  it('should have proper table structure', () => {
    const { container } = render(<TableSkeleton />);
    const table = container.firstChild;
    
    expect(table).toHaveClass('bg-white', 'rounded-lg', 'overflow-hidden');
  });
});

describe('FormSkeleton Component', () => {
  it('should render form with default number of fields', () => {
    const { container } = render(<FormSkeleton />);
    const fields = container.querySelectorAll('div > .mb-2');
    
    expect(fields).toHaveLength(4); // Default fields
  });

  it('should render custom number of fields', () => {
    const { container } = render(<FormSkeleton fields={6} />);
    const fields = container.querySelectorAll('div > .mb-2');
    
    expect(fields).toHaveLength(6);
  });

  it('should render form buttons', () => {
    const { container } = render(<FormSkeleton />);
    const buttonContainer = container.querySelector('.flex.space-x-3.pt-4');
    
    expect(buttonContainer).toBeInTheDocument();
    
    const buttons = buttonContainer.querySelectorAll('.h-10');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

describe('TextSkeleton Component', () => {
  it('should render default number of lines', () => {
    const { container } = render(<TextSkeleton />);
    const lines = container.querySelectorAll('.h-4');
    
    expect(lines).toHaveLength(3); // Default lines
  });

  it('should render custom number of lines', () => {
    const { container } = render(<TextSkeleton lines={5} />);
    const lines = container.querySelectorAll('.h-4');
    
    expect(lines).toHaveLength(5);
  });

  it('should apply custom widths', () => {
    const customWidths = ['w-full', 'w-3/4', 'w-1/2'];
    const { container } = render(<TextSkeleton lines={3} widths={customWidths} />);
    
    const lines = container.querySelectorAll('.h-4');
    expect(lines[0]).toHaveClass('w-full');
    expect(lines[1]).toHaveClass('w-3/4');
    expect(lines[2]).toHaveClass('w-1/2');
  });
});

describe('ChartSkeleton Component', () => {
  it('should render chart skeleton structure', () => {
    const { container } = render(<ChartSkeleton />);
    
    // Should have card wrapper
    expect(container.firstChild).toHaveClass('card');
    
    // Should have title area
    const titleArea = container.querySelector('.flex.items-center.justify-between.mb-6');
    expect(titleArea).toBeInTheDocument();
    
    // Should have chart area
    const chartArea = container.querySelector('.h-64.flex.items-end');
    expect(chartArea).toBeInTheDocument();
    
    // Should have legend area
    const legendArea = container.querySelector('.flex.justify-center.space-x-4.mt-4');
    expect(legendArea).toBeInTheDocument();
  });

  it('should render chart bars', () => {
    const { container } = render(<ChartSkeleton />);
    const bars = container.querySelectorAll('.w-8.rounded-t');
    
    expect(bars).toHaveLength(7); // Default number of bars
  });

  it('should render legend items', () => {
    const { container } = render(<ChartSkeleton />);
    const legendItems = container.querySelectorAll('.flex.items-center.space-x-2');
    
    expect(legendItems).toHaveLength(3); // Default legend items
  });
});