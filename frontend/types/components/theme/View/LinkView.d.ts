export default LinkView;
declare function LinkView({ token, content }: {
    token: any;
    content: any;
}): JSX.Element;
declare namespace LinkView {
    namespace propTypes {
        let content: PropTypes.Requireable<PropTypes.InferProps<{
            title: PropTypes.Requireable<string>;
            description: PropTypes.Requireable<string>;
            remoteUrl: PropTypes.Requireable<string>;
        }>>;
        let token: PropTypes.Requireable<string>;
    }
    namespace defaultProps {
        let content_1: any;
        export { content_1 as content };
        let token_1: any;
        export { token_1 as token };
    }
}
import PropTypes from 'prop-types';
